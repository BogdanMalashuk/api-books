from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from mongoengine.errors import DoesNotExist

from .models import Book, BorrowRecord, Genre, User
from .serializers import (
    BookSerializer,
    UserSerializer,
    GenreSerializer,
    BorrowRecordSerializer
)
from .permissions import IsAdminOrReadOnly


def get_object_or_404_mongo(cls, **kwargs):
    try:
        obj = cls.objects.get(**kwargs)
    except DoesNotExist:
        raise NotFound(detail=f"{cls.__name__} not found.")
    return obj


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        if not request.data.get('password'):
            return Response({'password': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"


class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = {
        'genre__name': ['exact'],
        'is_borrowed': ['exact'],
    }
    search_fields = ['author', 'published_at', 'title', 'genre']
    ordering_fields = ['title', 'author', 'published_at']
    ordering = ['title']


class BookDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        return get_object_or_404_mongo(Book, id=self.kwargs['pk'])


class GenreListCreateView(ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        return get_object_or_404_mongo(Genre, id=self.kwargs['pk'])


class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        book = get_object_or_404_mongo(Book, id=pk)
        if book.is_borrowed:
            return Response({"detail": "The book has already been taken"}, status=status.HTTP_400_BAD_REQUEST)

        BorrowRecord(user=request.user, book=book).save()
        return Response({"detail": "The book was successfully taken"}, status=status.HTTP_200_OK)


class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        book = get_object_or_404_mongo(Book, id=pk)
        try:
            record = BorrowRecord.objects.get(book=book, user=request.user, returned_at=None)
        except DoesNotExist:
            return Response({"detail": "You didn't take this book."}, status=status.HTTP_400_BAD_REQUEST)

        record.mark_returned()
        return Response({"detail": "Book successfully returned"}, status=status.HTTP_200_OK)


class UserBorrowedBooksView(ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id") or self.request.user.id
        if user_id != self.request.user.id and not self.request.user.is_staff:
            raise NotFound("You do not have permission to view other users' borrowed books.")
        borrow_records = BorrowRecord.objects(user=user_id, returned_at=None)
        return [record.book for record in borrow_records]


class BorrowHistoryView(ListAPIView):
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id") or self.request.user.id
        try:
            user = User.objects.get(id=user_id)
        except DoesNotExist:
            raise NotFound("User not found")

        if user.id != self.request.user.id and not self.request.user.is_staff:
            raise NotFound("You do not have permission to view this.")

        return BorrowRecord.objects.filter(user=user)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound
from .models import Book, BorrowRecord, Genre, User
from .serializers import BookSerializer, UserSerializer, GenreSerializer, BorrowRecordSerializer
from .permissions import IsAdminOrReadOnly
from mongoengine.errors import DoesNotExist


def get_object_or_404_mongo(cls, **kwargs):
    try:
        obj = cls.objects.get(**kwargs)
    except DoesNotExist:
        raise NotFound(detail=f"{cls.__name__} not found.")
    return obj


class RegisterView(APIView):
    def post(self, request):
        password = request.data.get('password')
        if not password:
            return Response({'password': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User successfully registered.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return User.objects.get(id=pk)
        except DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        books = Book.objects()
        genre = request.query_params.get("genre")
        author = request.query_params.get("author")
        is_borrowed = request.query_params.get("is_borrowed")

        if genre:
            books = books.filter(genre__name=genre)
        if author:
            books = books.filter(author__icontains=author)
        if is_borrowed is not None:
            is_borrowed_bool = is_borrowed.lower() in ['true', '1', 'yes']
            books = books.filter(is_borrowed=is_borrowed_bool)

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404_mongo(Book, id=pk)

    def get(self, request, pk):
        book = self.get_object(pk)
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        book = self.get_object(pk)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        book = get_object_or_404_mongo(Book, id=pk)
        if book.is_borrowed:
            return Response({"detail": "The book has already been taken"}, status=status.HTTP_400_BAD_REQUEST)

        record = BorrowRecord(user=request.user, book=book)
        record.save()
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


class UserBorrowedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id is None:
            user_id = request.user.id
        if user_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "You do not have permission to view other users' borrowed books."},
                            status=status.HTTP_403_FORBIDDEN)

        borrow_records = BorrowRecord.objects(user=user_id, returned_at=None)
        books = [record.book for record in borrow_records]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id is None:
            user = request.user
        else:
            try:
                user = User.objects.get(id=user_id)
            except DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            if request.user.id != user.id and not request.user.is_staff:
                return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)

        records = BorrowRecord.objects.filter(user=user)
        serializer = BorrowRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenreListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GenreSerializer(data=request.data)
        if serializer.is_valid():
            genre = Genre(**serializer.validated_data)
            genre.save()
            return Response(GenreSerializer(genre).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_genre(self, pk):
        try:
            return Genre.objects.get(id=pk)
        except DoesNotExist:
            return None

    def get(self, request, pk):
        genre = self.get_genre(pk)
        if not genre:
            return Response({"detail": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(GenreSerializer(genre).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        genre = self.get_genre(pk)
        if not genre:
            return Response({"detail": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GenreSerializer(genre, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(GenreSerializer(genre).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        genre = self.get_genre(pk)
        if not genre:
            return Response({"detail": "Genre not found"}, status=status.HTTP_404_NOT_FOUND)
        genre.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

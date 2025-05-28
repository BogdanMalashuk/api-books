from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<str:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<str:pk>/borrow/', BorrowBookView.as_view(), name='book-borrow'),
    path('books/<str:pk>/return/', ReturnBookView.as_view(), name='book-return'),

    path('genres/', GenreListCreateView.as_view(), name='genre-list-create'),
    path('genres/<str:pk>/', GenreDetailView.as_view(), name='genre-detail'),

    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/borrowed/', UserBorrowedBooksView.as_view(), name='self-borrowed'),
    path('users/<str:user_id>/borrowed/', UserBorrowedBooksView.as_view(), name='user-borrowed'),
    path('users/my-history/', BorrowHistoryView.as_view(), name='self-history'),
    path('users/<str:user_id>/history/', BorrowHistoryView.as_view(), name='user-history'),
]

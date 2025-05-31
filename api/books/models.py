from datetime import datetime, UTC
from django.contrib.auth.hashers import make_password, check_password
from mongoengine import (
    Document, StringField, ReferenceField, BooleanField,
    DateTimeField, EmailField
)


class User(Document):
    """
    Represents a user of the library system.
    """
    name = StringField(required=True, max_length=100)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """
        Hashes and sets the password.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Checks if the provided password matches the stored hash.
        """
        return check_password(raw_password, self.password)


class Genre(Document):
    """
    Represents a book genre/category.
    """
    name = StringField(required=True, max_length=50)

    def __str__(self):
        return self.name


class Book(Document):
    """
    Represents a book in the library.
    """
    title = StringField(required=True, max_length=200)
    author = StringField(required=True, max_length=100)
    description = StringField()
    genre = ReferenceField(Genre)
    is_borrowed = BooleanField(default=False)
    published_at = DateTimeField(default=datetime.now(UTC))

    def __str__(self):
        return self.title


class BorrowRecord(Document):
    """
    Represents a borrowing record of a book by a user.
    """
    user = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    borrowed_at = DateTimeField(default=datetime.now(UTC))
    returned_at = DateTimeField()

    def mark_returned(self):
        """
        Marks the book as returned and updates book availability.
        """
        self.returned_at = datetime.now(UTC)
        self.book.is_borrowed = False
        self.book.save()
        self.save()

    def save(self, *args, **kwargs):
        """
        Saves the borrowing record and sets book status to borrowed
        if not marked as returned yet.
        """
        if not self.returned_at:
            self.book.is_borrowed = True
            self.book.save()
        return super().save(*args, **kwargs)

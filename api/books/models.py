from datetime import datetime, UTC
from django.contrib.auth.hashers import make_password, check_password
from mongoengine import (
    Document, StringField, ReferenceField, BooleanField,
    DateTimeField, EmailField
)


class User(Document):
    name = StringField(required=True, max_length=100)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)  # здесь хранится хэш пароля

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Genre(Document):
    name = StringField(required=True, max_length=50)

    def __str__(self):
        return self.name


class Book(Document):
    title = StringField(required=True, max_length=200)
    author = StringField(required=True, max_length=100)
    description = StringField()
    genre = ReferenceField(Genre)
    is_borrowed = BooleanField(default=False)

    def __str__(self):
        return self.title


class BorrowRecord(Document):
    user = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    borrowed_at = DateTimeField(default=datetime.now(UTC))
    returned_at = DateTimeField()

    def mark_returned(self):
        self.returned_at = datetime.now(UTC)
        self.book.is_borrowed = False
        self.book.save()
        self.save()

    def save(self, *args, **kwargs):
        if not self.returned_at:
            self.book.is_borrowed = True
            self.book.save()
        return super().save(*args, **kwargs)

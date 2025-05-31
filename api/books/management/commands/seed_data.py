from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from books.models import User, Genre, Book, BorrowRecord


class Command(BaseCommand):
    """
    Django management command to populate the MongoDB database
    with sample data for testing and development.
    """
    help = 'Populates the database with test data'

    def handle(self, *args, **kwargs):
        BorrowRecord.objects.delete()
        Book.objects.delete()
        Genre.objects.delete()
        User.objects.delete()

        admin = User(name="Admin", email="admin@example.com")
        admin.set_password("adminpassword")
        admin.save()
        self.stdout.write(self.style.SUCCESS("Created superuser: admin@example.com / adminpassword"))

        users = []
        for i in range(1, 6):
            user = User(name=f"User{i}", email=f"user{i}@example.com")
            user.set_password(f"password{i}")
            user.save()
            users.append(user)

        genre_names = ["Science Fiction", "Detective", "Science", "Romance", "History"]
        genres = []
        for name in genre_names:
            genre = Genre(name=name)
            genre.save()
            genres.append(genre)

        book_data = [
            ("2001: A Space Odyssey", "Arthur C. Clarke", "A science fiction story about space exploration."),
            ("Sherlock Holmes", "Arthur Conan Doyle", "Detective stories featuring Sherlock Holmes."),
            ("The Feynman Lectures on Physics", "Richard Feynman", "Popular science physics lectures."),
            ("Pride and Passion", "Jane Austen", "A romantic novel."),
            ("World War II", "John Kennedy", "A historical study of the Second World War."),
        ]
        books = []
        for i, (title, author, description) in enumerate(book_data):
            book = Book(title=title, author=author, description=description, genre=genres[i])
            book.save()
            books.append(book)

        for i in range(5):
            borrowed_at = datetime.now(timezone.utc) - timedelta(days=i * 2)
            returned_at = None if i % 2 == 0 else borrowed_at + timedelta(days=1)
            record = BorrowRecord(
                user=users[i],
                book=books[i],
                borrowed_at=borrowed_at,
                returned_at=returned_at
            )
            record.save()

        self.stdout.write(self.style.SUCCESS("✅ Sample data successfully created!"))

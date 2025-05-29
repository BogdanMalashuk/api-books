from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from books.models import User, Genre, Book, BorrowRecord


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **kwargs):
        # Здесь твой код из функции seed() без os.environ и django.setup()
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
            u = User(name=f"User{i}", email=f"user{i}@example.com")
            u.set_password(f"password{i}")
            u.save()
            users.append(u)

        genres = []
        genre_names = ["Фантастика", "Детектив", "Научная литература", "Романтика", "История"]
        for name in genre_names:
            g = Genre(name=name)
            g.save()
            genres.append(g)

        books = []
        book_data = [
            ("Космическая одиссея", "Артур Кларк", "Фантастика о космосе"),
            ("Шерлок Холмс", "Артур Конан Дойл", "Детективные истории"),
            ("Физика для всех", "Ричард Фейнман", "Популярная наука"),
            ("Любовь и страсть", "Джейн Остин", "Романтический роман"),
            ("Вторая мировая", "Джон Кеннеди", "Историческое исследование"),
        ]
        for i, (title, author, desc) in enumerate(book_data):
            b = Book(title=title, author=author, description=desc, genre=genres[i])
            b.save()
            books.append(b)

        for i in range(5):
            borrowed_at = datetime.now(timezone.utc) - timedelta(days=i*2)
            returned_at = None if i % 2 == 0 else borrowed_at + timedelta(days=1)
            br = BorrowRecord(
                user=users[i],
                book=books[i],
                borrowed_at=borrowed_at,
                returned_at=returned_at
            )
            br.save()

        self.stdout.write(self.style.SUCCESS("✅ Тестовые данные успешно созданы!"))

from datetime import datetime, time, timedelta, timezone as dt_timezone

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from reading.models import Book, ReadingSession, Student

BOOKS = [
    ("The Hobbit", "J.R.R. Tolkien", 310),
    ("Holes", "Louis Sachar", 233),
    ("Wonder", "R.J. Palacio", 315),
    ("Matilda", "Roald Dahl", 240),
]


def at(days_ago: int, hour: int, minute: int = 0) -> datetime:
    """A UTC datetime `days_ago` days back from today, at the given UTC clock time."""
    today = datetime.now(dt_timezone.utc).date()
    return datetime.combine(
        today - timedelta(days=days_ago), time(hour, minute), tzinfo=dt_timezone.utc
    )


class Command(BaseCommand):
    help = "Loads a deterministic set of students, books and reading sessions."

    @transaction.atomic
    def handle(self, *args, **options):
        ReadingSession.objects.all().delete()
        Student.objects.all().delete()
        Book.objects.all().delete()

        books = [
            Book.objects.create(title=title, author=author, page_count=pages)
            for title, author, pages in BOOKS
        ]
        hobbit, holes, wonder, matilda = books

        ana = Student.objects.create(name="Ana", timezone="UTC")
        ben = Student.objects.create(name="Ben", timezone="UTC")
        cleo = Student.objects.create(name="Cleo", timezone="America/Lima")
        dai = Student.objects.create(name="Dai", timezone="UTC")
        Student.objects.create(name="Eve", timezone="UTC")
        finn = Student.objects.create(name="Finn", timezone="UTC")

        sessions = []

        # Ana: five days in a row, up to and including today.
        for days_ago in range(5):
            sessions.append((ana, hobbit if days_ago % 2 else holes, at(days_ago, 12), 25))

        # Ben: a four-day run, a gap, then two more days.
        for days_ago in (8, 7, 6, 5):
            sessions.append((ben, wonder, at(days_ago, 9), 40))
        for days_ago in (1, 0):
            sessions.append((ben, matilda, at(days_ago, 9), 15))

        # Cleo: two sessions ten minutes apart, either side of UTC midnight.
        sessions.append((cleo, matilda, at(1, 23, 50), 20))
        sessions.append((cleo, matilda, at(0, 0, 10), 20))

        # Dai: two sessions on the same day, plus one the day before.
        sessions.append((dai, holes, at(0, 8), 30))
        sessions.append((dai, holes, at(0, 20), 45))
        sessions.append((dai, wonder, at(1, 19), 10))

        # Eve: no sessions at all.

        # Finn: a six-day run that ended a month ago.
        for days_ago in range(30, 36):
            sessions.append((finn, hobbit, at(days_ago, 17), 55))

        ReadingSession.objects.bulk_create(
            ReadingSession(student=student, book=book, started_at=started_at, minutes=minutes)
            for student, book, started_at, minutes in sessions
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Student.objects.count()} students, "
                f"{Book.objects.count()} books, "
                f"{ReadingSession.objects.count()} sessions "
                f"(now: {timezone.now():%Y-%m-%d %H:%M %Z})."
            )
        )

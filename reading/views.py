from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import BookFilter, ReadingSessionFilter
from .models import Book, Student
from .serializers import BookSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference implementation. Follow this shape for the stats endpoint."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_class = BookFilter


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        student = self.get_object()#1st query
        sessions = student.sessions.all()

        session_filter = ReadingSessionFilter(
            data=request.query_params,
            queryset=sessions,
        )

        if not session_filter.is_valid():
            return Response(session_filter.errors, status=400)

        sessions = session_filter.qs

        book_stats = (
            sessions.values("book_id", "book__title")
            .annotate(
                minutes=Sum("minutes"),
                session_count=Count("id"),
            )
            .order_by("-minutes", "book_id")
        )
        books = [
            {
                "book_id": row["book_id"],
                "title": row["book__title"],
                "minutes": row["minutes"],
                "session_count": row["session_count"],
            }
            for row in book_stats #2nd query
        ]

        total_minutes = sum(book["minutes"] for book in books)

        student_timezone = ZoneInfo(student.timezone)

        read_dates = {#3rd query
            started_at.astimezone(student_timezone).date()
            for started_at in sessions.values_list("started_at", flat=True)
        }

        today = timezone.now().astimezone(student_timezone).date()
        current_streak = 0
        check_date = today

        # Walk backward from today until the first unread day.
        while check_date in read_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        longest_streak = 0
        running_streak = 0
        previous_date = None

        for read_date in sorted(read_dates):
            if (
                previous_date is not None
                and read_date == previous_date + timedelta(days=1)
            ):
                running_streak += 1
            else:
                running_streak = 1

            longest_streak = max(longest_streak, running_streak)
            previous_date = read_date

        return Response(
            {
                "student_id": student.pk,
                "total_minutes": total_minutes,
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "books": books,
            }
        )

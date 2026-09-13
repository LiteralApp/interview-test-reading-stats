from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum

from .filters import BookFilter
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
        student = self.get_object()
        sessions = student.sessions.all()

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
            for row in book_stats
        ]

        total_minutes = sum(book["minutes"] for book in books)

        return Response(
            {
                "student_id": student.pk,
                "total_minutes": total_minutes,
                "current_streak": 0,
                "longest_streak": 0,
                "books": books,
            }
        )
    
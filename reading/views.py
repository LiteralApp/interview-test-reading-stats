from rest_framework import viewsets

from .filters import BookFilter
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference implementation. Follow this shape for the stats endpoint."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_class = BookFilter

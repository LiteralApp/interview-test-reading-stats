from django_filters import rest_framework as filters

from .models import Book


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    """Allows ?id__in=1,2,3 style bulk filtering."""


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """Allows ?author__in=a,b style bulk filtering."""


class BookFilter(filters.FilterSet):
    id__in = NumberInFilter(field_name="id", lookup_expr="in")
    author__in = CharInFilter(field_name="author", lookup_expr="in")
    min_pages = filters.NumberFilter(field_name="page_count", lookup_expr="gte")

    class Meta:
        model = Book
        fields = ["author"]

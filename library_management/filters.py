import django_filters
from .models import Book, Author, Library, Category


class BookFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="author__name", lookup_expr="icontains"
    )
    library = django_filters.CharFilter(
        field_name="library__name", lookup_expr="icontains"
    )

    class Meta:
        model = Book
        fields = ["category", "author", "library"]

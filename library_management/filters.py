import django_filters
from django_filters import rest_framework as filters
from .models import Book, Author, Library, Category
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance


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


class AuthorFilter(django_filters.FilterSet):
    library = django_filters.CharFilter(method="filter_by_library")
    category = django_filters.CharFilter(method="filter_by_category")

    class Meta:
        model = Author
        fields = ["library", "category"]

    def filter_by_library(self, queryset, name, value):
        return Author.get_filtered_authors({"library": value})

    def filter_by_category(self, queryset, name, value):
        return Author.get_filtered_authors({"category": value})


class LibraryFilter(filters.FilterSet):
    radius = filters.NumberFilter(method="filter_by_user_location")
    category = filters.CharFilter(
        field_name="books__category__name", lookup_expr="icontains"
    )
    author = filters.CharFilter(
        field_name="books__author__name", lookup_expr="icontains"
    )

    class Meta:
        model = Library
        fields = ["category", "author", "radius"]

    def filter_by_user_location(self, queryset, name, value):
        try:
            user = self.request.user
            if not user.is_authenticated:
                return queryset

            user_location = user.userlocation.location
            if not user_location:
                return queryset

            radius = float(value or 10)

            return (
                queryset.filter(location__isnull=False)
                .annotate(distance=Distance("location", user_location))
                .filter(distance__lte=radius * 1000)
                .order_by("distance")
            )

        except (ValueError, AttributeError):
            return queryset

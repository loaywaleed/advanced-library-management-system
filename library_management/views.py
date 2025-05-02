from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.decorators import action
from .serializers import (
    BookSerializer,
    AuthorSerializer,
    CategorySerializer,
    LibrarySerializer,
    AuthorWithBooksSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BookFilter, LibraryFilter, AuthorFilter
from .models import Book, Author, Category, Library


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilter
    filterset_fields = ["category", "author"]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter

    def get_queryset(self):
        filters = {}
        if "library" in self.request.query_params:
            filters["library"] = self.request.query_params["library"]
        if "category" in self.request.query_params:
            filters["category"] = self.request.query_params["category"]
        return Author.get_filtered_authors(filters)

    @action(detail=False, methods=["GET"])
    def with_books(self, request):
        filters = {}
        for param in ["library", "category"]:
            if param in request.query_params:
                filters[param] = request.query_params[param]
        # get query
        fetched_query = Author.get_authors_with_books(filters)
        # pagination
        page = self.paginate_queryset(fetched_query)
        serializer = AuthorWithBooksSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

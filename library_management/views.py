from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
    IsAuthenticated,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    BookSerializer,
    AuthorSerializer,
    CategorySerializer,
    LibrarySerializer,
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

    @action(detail=False, methods=["GET"])
    def nearby(self, request):
        """Get nearby libraries"""
        try:
            radius = float(request.query_params.get("radius", 5))

            if not hasattr(request.user, "userlocation"):
                return Response({"error": "User location not set"}, status=400)

            nearby_libraries = request.user.userlocation.get_nearby_libraries(
                radius_km=radius
            )

            serializer = self.get_serializer(nearby_libraries, many=True)
            return Response(serializer.data)

        except ValueError:
            return Response({"error": "Invalid radius parameter"}, status=400)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

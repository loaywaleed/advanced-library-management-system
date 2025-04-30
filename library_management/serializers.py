from .models import Book, Author, Category, Library
from rest_framework import serializers


class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "bio", "book_count"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer()
    library_id = serializers.PrimaryKeyRelatedField(
        queryset=Library.objects.all(), source="library"
    )
    library_name = serializers.StringRelatedField(source="library", read_only=True)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class SimpleBookSerializer(serializers.ModelSerializer):
    """To use in Loaded Authors Serializer"""

    category = serializers.StringRelatedField(read_only=True)
    library_name = serializers.StringRelatedField(source="library", read_only=True)

    class Meta:
        model = Book
        fields = ["id", "title", "category", "library_name", "published_date", "isbn"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AuthorWithBooksSerializer(serializers.ModelSerializer):
    books = SimpleBookSerializer(many=True, read_only=True)
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "bio", "books", "book_count"]


class LibrarySerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(source="get_distance", read_only=True)

    class Meta:
        model = Library
        fields = ["id", "name", "address", "phone_number", "location", "distance"]

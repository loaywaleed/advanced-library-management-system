from .models import Book, Author, Category, Library
from rest_framework import serializers


class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "book_count"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    library_name = serializers.StringRelatedField(source="library", read_only=True)

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AuthorWithBooksSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "books", "book_count"]


class LibrarySerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True)

    class Meta:
        model = Library
        fields = ["id", "name", "address", "phone_number", "location", "distance"]

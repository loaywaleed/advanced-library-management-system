from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import date
from .models import BorrowingRecord
from library_management.serializers import SimpleBookSerializer
from library_management.models import Book


class BorrowingRecordOutputSerializer(serializers.ModelSerializer):
    book = SimpleBookSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    penalty_amount = serializers.DecimalField(
        max_digits=6, decimal_places=2, read_only=True
    )

    class Meta:
        model = BorrowingRecord
        fields = [
            "id",
            "book",
            "user",
            "borrowed_at",
            "due_date",
            "returned_at",
            "is_overdue",
            "penalty_amount",
        ]
        read_only_fields = fields


class BorrowingRecordInputSerializer(serializers.ModelSerializer):
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source="book", write_only=True
    )
    due_date = serializers.DateField(required=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BorrowingRecord
        fields = ["book_id", "due_date", "user"]

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value

    def create(self, validated_data):
        try:
            return BorrowingRecord.create_borrowing(
                book=validated_data["book"],
                user=validated_data["user"],
                due_date=validated_data["due_date"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

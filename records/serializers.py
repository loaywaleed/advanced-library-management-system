from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import date
from .models import BorrowingRecord
from library_management.serializers import BookSerializer
from library_management.models import Book


class BorrowingRecordOutputSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
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


class BulkBorrowingInputSerializer(serializers.Serializer):
    book_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Book.objects.all()),
        allow_empty=False,
        write_only=True,
    )
    due_date = serializers.DateField(required=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value

    def validate_book_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Duplicate book IDs are not allowed in a single request."
            )
        return value


class BulkReturnInputSerializer(serializers.Serializer):
    record_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=BorrowingRecord.objects.filter(returned_at__isnull=True)
        ),
        allow_empty=False,
        write_only=True,
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_record_ids(self, value):
        # Ensure all provided record IDs belong to the current user
        user = self.context["request"].user
        user_records_count = BorrowingRecord.objects.filter(
            id__in=[record.id for record in value], user=user, returned_at__isnull=True
        ).count()
        if user_records_count != len(value):
            raise serializers.ValidationError(
                "One or more invalid or already returned record IDs provided."
            )
        return value

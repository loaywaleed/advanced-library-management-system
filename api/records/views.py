import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from .models import BorrowingRecord
from .serializers import (
    BorrowingRecordOutputSerializer,
    BulkBorrowingInputSerializer,
    BulkReturnInputSerializer,
)
from .services import BorrowingService

logger = logging.getLogger(__name__)


class BorrowingRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing borrowing records using ModelViewSet with overrides.
    Uses Service Layer for business logic.
    - POST /borrowings/: Bulk borrow books.
    - GET /borrowings/: List user's borrowing records.
    - GET /borrowings/{id}/: Retrieve a specific record.
    - DELETE /borrowings/{id}/: Delete a specific record.
    - PUT /borrowings/{id}/: Not Allowed.
    - PATCH /borrowings/{id}/: Not Allowed.
    Includes a custom action for bulk returning books.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return borrowing records for the currently authenticated user."""
        return BorrowingRecord.objects.select_related(
            "book", "book__author", "book__category", "book__library", "user"
        ).filter(user=self.request.user)

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action == "create":
            return BulkBorrowingInputSerializer
        if self.action == "return_multiple":
            return BulkReturnInputSerializer
        return BorrowingRecordOutputSerializer

    def create(self, request, *args, **kwargs):
        """Overrides create action to handle bulk borrowing via Service Layer."""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        book_ids = [book.id for book in validated_data["book_ids"]]
        due_date = validated_data["due_date"]
        user = request.user

        try:
            created_records = BorrowingService.borrow_books(
                user=user, book_ids=book_ids, due_date=due_date
            )
            output_serializer = BorrowingRecordOutputSerializer(
                created_records, many=True, context=self.get_serializer_context()
            )
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_detail = (
                e.detail
                if hasattr(e, "detail")
                else (e.message_dict if hasattr(e, "message_dict") else e.messages)
            )
            return Response(
                {"errors": error_detail}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error during create/borrow for user {user.id}: {e}"
            )
            return Response(
                {
                    "error": (
                        str(e)
                        if str(e)
                        else "An unexpected error occurred during borrowing."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "PUT" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "PATCH" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["POST"], url_path="return-multiple")
    def return_multiple(self, request):
        """Handles bulk return via Service Layer."""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        record_ids_to_return = [
            record.id for record in serializer.validated_data["record_ids"]
        ]

        try:
            returned_records = BorrowingService.return_records(
                record_ids=record_ids_to_return
            )
            output_serializer = BorrowingRecordOutputSerializer(
                returned_records, many=True, context=self.get_serializer_context()
            )
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            error_detail = (
                e.detail
                if hasattr(e, "detail")
                else (e.message_dict if hasattr(e, "message_dict") else e.messages)
            )
            return Response(
                {"errors": error_detail}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(
                f"Unexpected error during return_multiple for record IDs {record_ids_to_return}: {e}"
            )
            return Response(
                {
                    "error": (
                        str(e)
                        if str(e)
                        else "An unexpected error occurred during return."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

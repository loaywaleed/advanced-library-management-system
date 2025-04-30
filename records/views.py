from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError

from .models import BorrowingRecord
from .serializers import (
    BorrowingRecordOutputSerializer,
    BorrowingRecordInputSerializer,
)


class BorrowingRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return BorrowingRecord.objects.select_related(
            "book", "book__author", "book__category", "book__library", "user"
        )

    def get_serializer_class(self):
        if self.action in ["create"]:
            return BorrowingRecordInputSerializer
        return BorrowingRecordOutputSerializer

    @action(detail=True, methods=["POST"])
    def return_book(self, request, pk=None):
        try:
            record = self.get_object()
            returned_record = record.return_book()
            serializer = BorrowingRecordOutputSerializer(returned_record)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

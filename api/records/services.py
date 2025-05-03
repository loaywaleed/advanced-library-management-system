from datetime import date, timedelta
import os
from django.db import transaction, DatabaseError
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from api.library_management.models import Book
from .models import BorrowingRecord
from .tasks import send_borrowing_confirmation


class BorrowingService:
    """Service for handling the business logic for borrowing and returning books."""

    @staticmethod
    def _validate_borrowing_limit(user, num_books_to_borrow):
        """Protected method to check the borrowing limit for a user"""
        active_borrowings = BorrowingRecord.objects.filter(
            user=user, returned_at__isnull=True
        ).count()
        if (
            active_borrowings + num_books_to_borrow
        ) > BorrowingRecord.MAX_BOOKS_PER_USER:
            allowed = BorrowingRecord.MAX_BOOKS_PER_USER - active_borrowings
            raise ValidationError(
                f"Cannot borrow {num_books_to_borrow} more books. "
                f"You have {active_borrowings} active borrowings. "
                f"You can borrow {max(0, allowed)} more."
            )

    @staticmethod
    def _validate_due_date(due_date):
        """Protected method to check the due date for a borrowing request"""
        max_due_date = date.today() + timedelta(days=30)
        if due_date > max_due_date:
            raise ValidationError(f"Due date cannot be more than 30 days from now")
        if due_date < date.today():
            raise ValidationError("Due date cannot be in the past")

    @staticmethod
    @transaction.atomic
    def borrow_books(user, book_ids, due_date):
        num_books = len(book_ids)
        if num_books == 0:
            raise ValidationError("No book IDs provided.")
        distinct_book_ids = list(set(book_ids))
        if len(distinct_book_ids) != num_books:
            num_books = len(distinct_book_ids)
        BorrowingService._validate_borrowing_limit(user, num_books)
        BorrowingService._validate_due_date(due_date)
        records_to_create = []
        try:
            locked_books = list(
                Book.objects.select_for_update().filter(id__in=distinct_book_ids)
            )
            locked_books_dict = {b.id: b for b in locked_books}
            if len(locked_books) != len(distinct_book_ids):
                missing_ids = set(distinct_book_ids) - set(locked_books_dict.keys())
                raise ValidationError(
                    f"One or more requested books do not exist. Missing IDs: {missing_ids}"
                )
            for book_id in distinct_book_ids:
                book = locked_books_dict[book_id]
                if book.available_copies < 1:
                    raise ValidationError(
                        f"Book '{book.title}' (ID: {book.id}) is not available."
                    )
                records_to_create.append(
                    BorrowingRecord(book=book, user=user, due_date=due_date)
                )
                book.available_copies -= 1
            created_records = BorrowingRecord.objects.bulk_create(records_to_create)
            Book.objects.bulk_update(locked_books, ["available_copies"])
            borrowing_ids = [record.id for record in created_records]
            if os.getenv("DJANGO_ENV") == "development":
                send_borrowing_confirmation.delay(borrowing_ids)
            return created_records
        except DatabaseError as e:
            raise ValidationError(
                "Could not process borrowing request due to a database issue. Please try again."
            )
        except ValidationError:
            raise
        except Exception as e:
            raise Exception("An unexpected error occurred during borrowing.")

    @staticmethod
    @transaction.atomic
    def return_records(record_ids):
        if not record_ids:
            raise ValidationError("No record IDs provided for return.")
        distinct_record_ids = list(set(record_ids))
        returned_records_update_list = []
        book_ids_to_increment = []
        now = timezone.now()
        try:
            locked_records = list(
                BorrowingRecord.objects.select_related("book")
                .select_for_update(of=("self", "book"))
                .filter(id__in=distinct_record_ids)
            )
            locked_records_dict = {r.id: r for r in locked_records}
            if len(locked_records) != len(distinct_record_ids):
                missing_ids = set(distinct_record_ids) - set(locked_records_dict.keys())
                raise ValidationError(
                    f"One or more borrowing records not found or inaccessible. Missing/Inaccessible IDs: {missing_ids}"
                )
            # Prepare updates
            for record_id in distinct_record_ids:
                record = locked_records_dict[record_id]
                if record.returned_at:
                    raise ValidationError(
                        f"Record ID {record.id} for book '{record.book.title}' has already been returned."
                    )
                record.returned_at = now
                overdue_days = 0
                if record.due_date < now.date():
                    overdue_days = (now.date() - record.due_date).days
                record.penalty_amount = max(
                    0, overdue_days * float(BorrowingRecord.DAILY_PENALTY)
                )
                returned_records_update_list.append(record)
                book_ids_to_increment.append(record.book_id)
            # Perform bulk updates
            BorrowingRecord.objects.bulk_update(
                returned_records_update_list, ["returned_at", "penalty_amount"]
            )
            if book_ids_to_increment:
                Book.objects.filter(id__in=book_ids_to_increment).update(
                    available_copies=F("available_copies") + 1
                )
            return returned_records_update_list
        except DatabaseError as e:
            raise ValidationError(
                "Could not process return request due to a database issue. Please try again."
            )
        except ValidationError:
            raise
        except Exception as e:
            raise Exception("An unexpected error occurred during return.")

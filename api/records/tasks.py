# records/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import BorrowingRecord
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_borrowing_confirmation(borrowing_ids):
    """
    Send confirmation emails for borrowings
    """
    try:
        borrowings = BorrowingRecord.objects.filter(
            id__in=borrowing_ids
        ).select_related("user", "book")
        for borrowing in borrowings:
            if not borrowing.user.email:
                logger.warning(
                    f"No email for user {borrowing.user.username} in borrowing {borrowing.id}"
                )
                continue
            subject = "Book Borrowing Confirmation"
            message = (
                f"Dear {borrowing.user.username},\n\n"
                f"You have successfully borrowed '{borrowing.book.title}'. "
                f"Please return by {borrowing.due_date.strftime('%Y-%m-%d')}.\n\n"
                f"Thank you!"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [borrowing.user.email],
                fail_silently=False,
            )
    except Exception as e:
        logger.error(
            f"Error sending confirmation emails for borrowings {borrowing_ids}: {e}"
        )
        raise  # Re-raise to allow Celery retries


@shared_task
def send_borrowing_reminders():
    """
    Send daily reminders for borrowings due within the next 3 days.
    """
    try:
        today = datetime.now().date()
        reminder_threshold = today + timedelta(days=3)
        borrowings = BorrowingRecord.objects.filter(
            returned_at__isnull=True,
            due_date__lte=reminder_threshold,
            due_date__gte=today,
        ).select_related("user", "book")

        for borrowing in borrowings:
            if not borrowing.user.email:
                logger.warning(
                    f"No email for user {borrowing.user.username} in borrowing {borrowing.id}"
                )
                continue
            subject = "Book Return Reminder"
            message = (
                f"Dear {borrowing.user.username},\n\n"
                f"Your borrowing of '{borrowing.book.title}' is due on "
                f"{borrowing.due_date.strftime('%Y-%m-%d')}. "
                f"Please return it on time to avoid penalties.\n\n"
                f"Thank you!"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [borrowing.user.email],
                fail_silently=False,
            )
    except Exception as e:
        logger.error(f"Error sending reminder emails: {e}")
        raise

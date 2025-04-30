from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, date


class BorrowingRecord(models.Model):
    DAILY_PENALTY = 10.00
    MAX_BOOKS_PER_USER = 3

    book = models.ForeignKey(
        "library_management.Book", on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="borrowings"
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    penalty_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    @classmethod
    def can_borrow(cls, user):
        # fetch active borrowings
        active_borrowings = cls.objects.filter(
            user=user, returned_at__isnull=True
        ).count()
        if active_borrowings >= cls.MAX_BOOKS_PER_USER:
            raise ValidationError(
                f"Cannot borrow more than {cls.MAX_BOOKS_PER_USER} books at once"
            )
        return True

    @classmethod
    def create_borrowing(cls, book, user, due_date):
        # checking if we can borrow
        cls.can_borrow(user)

        # due date validation
        max_due_date = date.today() + timedelta(days=30)
        if due_date > max_due_date:
            raise ValidationError("Due date cannot be more than 30 days from now")

        return cls.objects.create(book=book, user=user, due_date=due_date)

    def calculate_penalty(self):
        if not self.returned_at or not self.is_overdue():
            return 0

        overdue_days = (self.returned_at - self.due_date).days
        return max(0, overdue_days * self.DAILY_PENALTY)

    def is_overdue(self):
        if self.returned_at:
            return self.returned_at > self.due_date
        return date.today() > self.due_date

    def return_book(self):
        if self.returned_at:
            raise ValidationError("Book already returned")

        self.returned_at = timezone.now()
        self.penalty_amount = self.calculate_penalty()
        self.save()
        return self

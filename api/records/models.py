from django.db import models
from datetime import date


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

    def calculate_penalty(self):
        """Calculates penalty based on return date and due date."""
        if not self.returned_at or self.due_date >= self.returned_at.date():
            return 0.00
        overdue_days = (self.returned_at.date() - self.due_date).days
        return max(0.00, overdue_days * float(self.DAILY_PENALTY))

    def is_overdue(self):
        """Checks if the borrowing record is overdue."""
        current_check_date = (
            self.returned_at.date() if self.returned_at else date.today()
        )
        return current_check_date > self.due_date

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

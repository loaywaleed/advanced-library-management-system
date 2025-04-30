from django.db import models


class BorrowingRecord(models.Model):
    book = models.ForeignKey(
        "Book", on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="borrowings"
    )
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} borrowed {self.book} on {self.borrowed_at}"

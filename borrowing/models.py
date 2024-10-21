from datetime import date

from django.core.exceptions import ValidationError
from django.db import models

from book.models import Book
from library_api import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(default=date.today)
    expected_return = models.DateField()
    actual_return = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def __str__(self):
        return f"{self.book.title} - {self.expected_return}"

    @property
    def is_active(self):
        return self.actual_return is None

    def clean(self):
        if self.expected_return.day <= self.borrow_date.day:
            raise ValidationError(
                f"Expected return date must be after {self.borrow_date}"
            )
        if self.actual_return and self.actual_return < self.borrow_date:
            raise ValidationError(
                f"Actual return date must be after {self.borrow_date}"
            )

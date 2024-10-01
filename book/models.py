from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=256)
    author = models.CharField(max_length=256)
    cover = models.CharField(max_length=50, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(decimal_places=2, max_digits=7)

    def __str__(self):
        return f"{self.title} - author: {self.author}"

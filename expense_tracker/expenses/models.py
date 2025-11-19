from django.db import models
from django.contrib.auth.models import User


class Expense(models.Model):
    """
    Simple expense entry belonging to a single authenticated user.
    This stays intentionally small to make deployment across
    different orchestration environments straightforward.
    """

    CATEGORY_CHOICES = [
        ("FOOD", "Food"),
        ("TRANSPORT", "Transport"),
        ("ENTERTAINMENT", "Entertainment"),
        ("OTHER", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        """
        Human-readable representation used in the admin and debug logs.
        """
        return f"{self.name} ({self.category}) — {self.amount}"


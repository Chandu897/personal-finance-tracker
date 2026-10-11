from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    type = models.CharField(max_length=10)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return self.description
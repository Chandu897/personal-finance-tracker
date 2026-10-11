from django import forms
from .models import Transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class TransactionForm(forms.ModelForm):

    TYPE_CHOICES = [
        ("Income", "Income"),
        ("Expense", "Expense"),
    ]

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Travel", "Travel"),
        ("Bills", "Bills"),
        ("Shopping", "Shopping"),
        ("Education", "Education"),
        ("Other", "Other"),
    ]

    type = forms.ChoiceField(choices=TYPE_CHOICES)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        model = Transaction
        fields = [
            "amount",
            "type",
            "category",
            "description",
            "date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["amount"].widget.attrs.update({
            "placeholder": "Enter amount",
            "min": "0.01",
            "step": "0.01",
        })

        self.fields["description"].widget.attrs.update({
            "placeholder": "What was this transaction for?",
        })

        self.fields["date"].widget = forms.DateInput(
            attrs={"type": "date"}
        )


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            "username",
            "password1",
            "password2",
        ]
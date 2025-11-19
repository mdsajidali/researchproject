from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Expense


class UserRegistrationForm(UserCreationForm):
    """
    Registration form that extends Django's built-in UserCreationForm
    by requiring an email address.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ExpenseForm(forms.ModelForm):
    """
    Form used for both creating and editing Expense instances.
    """

    class Meta:
        model = Expense
        fields = ["name", "amount", "date", "category", "description"]
        widgets = {
            # Keeps the UI simple and consistent across environments.
            "date": forms.SelectDateWidget(),
        }

    def clean_amount(self):
        """
        Ensure the user cannot accidentally submit a negative amount.
        """
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount < 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount


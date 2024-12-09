from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Expense

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Ensure email is required

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Expense Form
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date', 'category', 'description']  # Include the fields you want to capture from the user
        widgets = {
            'date': forms.SelectDateWidget(),  # This gives a date picker in the form
        }

    # Adding custom validation
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount


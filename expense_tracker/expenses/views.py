from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

import calendar
import json

from .forms import ExpenseForm, UserRegistrationForm
from .models import Expense

<<<<<<< HEAD
#Only authenticated users can create new expenses
@login_required(login_url='/login/')
=======

def _get_user_expenses(user):
    """
    Return a queryset of expenses for the given user.

    Anonymous users simply get an empty queryset so that the view
    can safely render the public landing page.
    """
    if not user.is_authenticated:
        return Expense.objects.none()
    return Expense.objects.filter(user=user).order_by("-date", "-id")


def _build_chart_data(expenses):
    """
    Prepare aggregated data for the charts (by category and by month).

    The structure of this dictionary matches what the JavaScript
    in the template expects:
        {
            "categories": [...],
            "category_totals": [...],
            "months": [...],
            "monthly_totals": [...]
        }
    """
    chart_data = {
        "categories": [],
        "category_totals": [],
        "months": [],
        "monthly_totals": [],
    }

    if not expenses.exists():
        return chart_data

    # Aggregate by category
    category_rows = (
        expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("category")
    )
    chart_data["categories"] = [row["category"] for row in category_rows]
    chart_data["category_totals"] = [
        float(row["total"]) for row in category_rows
    ]

    # Aggregate by month for the current year
    current_year = now().year
    monthly_rows = (
        expenses.filter(date__year=current_year)
        .values_list("date__month")
        .annotate(total=Sum("amount"))
        .order_by("date__month")
    )
    chart_data["months"] = [calendar.month_name[m] for m, _ in monthly_rows]
    chart_data["monthly_totals"] = [float(total) for _, total in monthly_rows]

    return chart_data


def expense_list(request):
    """
    Main page.

    - For authenticated users: show dashboard, charts and expense table.
    - For anonymous users: show a simple landing page with login/signup links.
    """
    expenses = _get_user_expenses(request.user)
    chart_data = _build_chart_data(expenses)

    context = {
        "expenses": expenses,
        "loggedin": request.user.is_authenticated,
        "chart_data": json.dumps(chart_data),
    }
    return render(request, "expenses/expense_list.html", context)


@login_required
>>>>>>> 6c094ffa2d5cd940adeaec09ed1d03bf5dc296d1
def expense_create(request):
    """
    Create a new expense entry for the current user.
    """
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Your expense has been recorded.")
            return redirect("expense_list")
    else:
        form = ExpenseForm()

    context = {
        "form": form,
        "form_title": "Add a new expense",
        "button_text": "Save expense",
    }
    return render(request, "expenses/expense_form.html", context)


@login_required
def expense_update(request, id):
    """
    Update an existing expense belonging to the current user.
    """
    expense = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Your changes have been saved.")
            return redirect("expense_list")
    else:
        form = ExpenseForm(instance=expense)

    context = {
        "form": form,
        "form_title": "Edit expense",
        "button_text": "Update",
    }
    return render(request, "expenses/expense_form.html", context)


@login_required
def expense_delete(request, id):
    """
    Delete an expense owned by the current user.

    In this simple app we perform the delete immediately and then
    send the user back to the list.
    """
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect("expense_list")


def signup_view(request):
    """
    Handle user registration and log the new user in immediately.
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Your account has been created. You can now start tracking expenses.",
            )
            return redirect("expense_list")
        else:
            messages.error(request, "We could not create your account. Please check the form.")
    else:
        form = UserRegistrationForm()

    return render(request, "expenses/signup.html", {"form": form})


def login_view(request):
    """
    Basic username/password login.
    """
    if request.user.is_authenticated:
        # Already logged in, go straight to the dashboard.
        return redirect("expense_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("expense_list")
            messages.error(request, "The username or password did not match.")
        else:
            messages.error(request, "Please check the details you entered.")
    else:
        form = AuthenticationForm()

    return render(request, "expenses/login.html", {"form": form})


def logout_view(request):
    """
    Log the current user out and send them back to the login screen.
    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


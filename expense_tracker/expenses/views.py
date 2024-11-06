# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib import messages
from django.db.models import Sum
from django.utils.timezone import now
import calendar
import json


def expense_list(request):
    
    expenses=None
    chart_data = {}
    
    if  request.user.is_authenticated:
        #return redirect('login')
        expenses = Expense.objects.filter(user=request.user)
        
# Calculate total expenses by category
        category_data = expenses.values('category').annotate(total=Sum('amount'))
        chart_data['categories'] = [item['category'] for item in category_data]
        chart_data['category_totals'] = [float(item['total']) for item in category_data]  # Convert Decimal to float
        
        # Calculate total expenses by month
        current_year = now().year
        monthly_data = expenses.filter(date__year=current_year).values_list('date__month').annotate(total=Sum('amount'))
        chart_data['months'] = [calendar.month_name[month[0]] for month in monthly_data]
        chart_data['monthly_totals'] = [float(month[1]) for month in monthly_data]  # Convert Decimal to float
    
    context = {
        'expenses': expenses,
        'loggedin': request.user.is_authenticated,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'expenses/expense_list.html', context)
    
'''def home_view(request):
    #if not request.user.is_authenticated:
        return render(request,'expenses/home_page.html')'''  # Redirect to the expense list if logged in


def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense created successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'form_title': 'Add New Expense', 'button_text': 'Save Expense'})


def expense_update(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'form_title': 'Edit Expense', 'button_text': 'Update Expense'})


def expense_delete(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect('expense_list')

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('login')
        else:
            messages.error(request, "Signup failed. Please try again.")
    else:
        form = UserRegistrationForm()
    return render(request, 'expenses/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('expense_list')  # Redirect authenticated users to the home page
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('expense_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'expenses/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login') #Redirecting again to the login page

from django.urls import path

from . import views

urlpatterns = [
    path("", views.expense_list, name="expense_list"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("add/", views.expense_create, name="expense_create"),
    path("edit/<int:id>/", views.expense_update, name="expense_update"),
    path("delete/<int:id>/", views.expense_delete, name="expense_delete"),
]


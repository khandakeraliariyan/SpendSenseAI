from django.urls import path
from .views import expense_list, delete_expense

urlpatterns = [
    path("expenses/", expense_list, name="expenses"),
    path("expenses/delete/<int:id>/", delete_expense, name="delete_expense"),
]

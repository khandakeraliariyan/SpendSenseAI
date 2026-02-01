from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-created_at")

    if request.method == "POST":
        title = request.POST["title"]
        amount = request.POST["amount"]
        category = request.POST["category"]

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category
        )

        return redirect("expenses")

    return render(request, "expenses.html", {"expenses": expenses})


@login_required
def delete_expense(request, id):
    expense = Expense.objects.get(id=id, user=request.user)
    expense.delete()
    return redirect("expenses")

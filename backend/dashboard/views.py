from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expenses.models import Expense
from django.db.models import Sum
from datetime import date

@login_required
def dashboard_view(request):
    expenses = Expense.objects.filter(user=request.user)

    total_spent = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    count = expenses.count()

    today = date.today()
    first_expense = expenses.order_by("created_at").first()

    if first_expense:
        days = (today - first_expense.created_at.date()).days + 1
    else:
        days = 1

    avg_per_day = round(total_spent / days, 2)

    context = {
        "total_spent": round(total_spent, 2),
        "count": count,
        "avg_per_day": avg_per_day,
    }

    return render(request, "dashboard.html", context)

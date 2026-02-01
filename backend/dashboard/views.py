from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expenses.models import Expense
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

@login_required
def dashboard_view(request):

    today = timezone.now().date()

    # -------- WEEKLY --------
    week_ago = today - timedelta(days=6)

    weekly_expenses = Expense.objects.filter(
        user=request.user,
        created_at__date__gte=week_ago
    )

    weekly_total = weekly_expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    daily = (
        weekly_expenses
        .extra({'day': "date(created_at)"})
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )

    biggest_day = daily.order_by("-total").first()

    # -------- PREDICTION --------
    daily_avg = weekly_total / 7 if weekly_total else 0
    predicted_month = round(daily_avg * 30, 2)

    # -------- MONTHLY --------

    monthly_expenses = Expense.objects.filter(
        user=request.user,
        created_at__month=today.month,
        created_at__year=today.year
    )

    monthly_total = monthly_expenses.aggregate(Sum("amount"))["amount__sum"] or 0

    categories = (
        monthly_expenses
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    biggest_category = categories.first()

    # -------- AI LITE (RULE BASED) --------

    waste_category = biggest_category["category"] if biggest_category else "None"
    waste_amount = round(biggest_category["total"], 2) if biggest_category else 0

    tips = []

    if waste_category == "Food":
        tips.append("Reduce eating outside — cook at home twice a week.")
    elif waste_category == "Transport":
        tips.append("Try walking or public transport for short trips.")
    elif waste_category == "Shopping":
        tips.append("Avoid impulse purchases — wait 24 hours before buying.")
    else:
        tips.append("Track small expenses — they add up quickly.")

    tips.append("Set a weekly spending limit and stick to it.")
    tips.append("Save at least 10% of your income every month.")

    estimated_saving = round(waste_amount * 0.2, 2)

    context = {
        "weekly_total": round(weekly_total, 2),
        "daily": daily,
        "biggest_day": biggest_day,

        "predicted_month": predicted_month,

        "monthly_total": round(monthly_total, 2),
        "categories": categories,
        "biggest_category": biggest_category,

        "waste_category": waste_category,
        "waste_amount": waste_amount,
        "tips": tips,
        "estimated_saving": estimated_saving,
    }

    return render(request, "dashboard.html", context)

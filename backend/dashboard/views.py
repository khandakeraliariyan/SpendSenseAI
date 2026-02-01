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

    context = {
        "weekly_total": round(weekly_total, 2),
        "daily": daily,
        "biggest_day": biggest_day,

        "monthly_total": round(monthly_total, 2),
        "categories": categories,
        "biggest_category": biggest_category,
    }

    return render(request, "dashboard.html", context)

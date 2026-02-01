from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from datetime import timedelta, date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Expense


# ============================
# EXPENSE CRUD
# ============================

@login_required
def expense_list(request):

    if request.method == "POST":
        title = request.POST.get("title")
        amount = request.POST.get("amount")
        category = request.POST.get("category")

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category
        )

        return redirect("/expenses/")

    expenses = Expense.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "expenses.html", {
        "expenses": expenses
    })


@login_required
def delete_expense(request, id):
    Expense.objects.filter(id=id, user=request.user).delete()
    return redirect("/expenses/")


# ============================
# DASHBOARD
# ============================

@login_required
def dashboard(request):

    today = date.today()
    week_ago = today - timedelta(days=7)

    expenses = Expense.objects.filter(user=request.user)

    # LAST 7 DAYS
    weekly = expenses.filter(created_at__date__gte=week_ago)

    weekly_total = weekly.aggregate(Sum("amount"))["amount__sum"] or 0

    daily = weekly.values("created_at__date").annotate(
        total=Sum("amount")
    ).order_by("-created_at__date")

    biggest_day = daily.first()

    # MONTHLY
    monthly = expenses.filter(
        created_at__year=today.year,
        created_at__month=today.month
    )

    monthly_total = monthly.aggregate(Sum("amount"))["amount__sum"] or 0

    categories = monthly.values("category").annotate(
        total=Sum("amount")
    ).order_by("-total")

    biggest_category = categories.first()

    # SIMPLE PREDICTION
    predicted_month = round((weekly_total / 7) * 30, 2) if weekly_total else 0

    return render(request, "dashboard.html", {
        "weekly_total": weekly_total,
        "daily": [
            {"day": str(d["created__date"]), "total": d["total"]}
            for d in daily
        ],
        "biggest_day": {
            "day": str(biggest_day["created__date"]),
            "total": biggest_day["total"]
        } if biggest_day else None,

        "monthly_total": monthly_total,
        "categories": categories,
        "biggest_category": biggest_category,
        "predicted_month": predicted_month,
    })


# ============================
# PDF EXPORT
# ============================

@login_required
def export_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    expenses = Expense.objects.filter(user=request.user)

    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Expense Report - {request.user.username}")

    y -= 30
    p.setFont("Helvetica", 10)

    total = 0

    for e in expenses:
        line = f"{e.title} | {e.category} | ৳ {e.amount}"
        p.drawString(50, y, line)
        total += e.amount
        y -= 15

        if y < 50:
            p.showPage()
            y = height - 50

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Spent: ৳ {round(total,2)}")

    p.showPage()
    p.save()

    return response

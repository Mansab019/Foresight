from django.shortcuts import render, redirect

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from dateutil.relativedelta import relativedelta
from core.models import Transaction, Budget, Prediction, Alert
from core.ml.pipeline import run_ml_pipeline
from core.alerts import generate_alerts
from django.contrib.auth.models import User


# ── LOGIN ─────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── DASHBOARD ─────────────────────────────────────────
@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    current_month = today.replace(day=1)
    next_month = current_month + relativedelta(months=1)

    # Total spent this month
    total_spent = Transaction.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total budget this month
    total_budget = Budget.objects.filter(
        user=user,
        month=current_month
    ).aggregate(total=Sum('monthly_limit'))['total'] or 0

    # Unread alerts count
    alert_count = Alert.objects.filter(
        user=user, is_read=False
    ).count()

    # Total transactions
    total_transactions = Transaction.objects.filter(user=user).count()

    # Spending by category this month for chart
    category_spending = Transaction.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date')[:8]

    # Recent alerts
    recent_alerts = Alert.objects.filter(
        user=user, is_read=False
    ).order_by('-created_at')[:5]

    # Predictions for next month
    predictions = Prediction.objects.filter(
        user=user,
        prediction_month=next_month
    )

    context = {
        'total_spent':        round(total_spent, 2),
        'total_budget':       round(total_budget, 2),
        'alert_count':        alert_count,
        'total_transactions': total_transactions,
        'category_spending':  list(category_spending),
        'recent_transactions':recent_transactions,
        'recent_alerts':      recent_alerts,
        'predictions':        predictions,
    }
    return render(request, 'core/dashboard.html', context)


# ── EXPENSES ──────────────────────────────────────────
@login_required
def expenses(request):
    user = request.user

    if request.method == 'POST':
        Transaction.objects.create(
            user=user,
            amount=request.POST['amount'],
            category=request.POST['category'],
            description=request.POST.get('description', ''),
            date=request.POST['date'],
            source='manual'
        )
        messages.success(request, 'Expense added successfully!')
        return redirect('expenses')

    transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date')[:50]

    alert_count = Alert.objects.filter(
        user=user, is_read=False
    ).count()

    categories = [
        'food', 'transport', 'rent', 'utilities',
        'entertainment', 'healthcare', 'shopping',
        'education', 'other'
    ]

    return render(request, 'core/expenses.html', {
        'transactions': transactions,
        'categories':   categories,
        'alert_count':  alert_count,
    })


# ── PREDICTIONS ───────────────────────────────────────
@login_required
def predictions_view(request):
    user = request.user
    today = date.today()
    next_month = today.replace(day=1) + relativedelta(months=1)

    predictions = Prediction.objects.filter(
        user=user,
        prediction_month=next_month
    ).order_by('-predicted_amount')

    alert_count = Alert.objects.filter(
        user=user, is_read=False
    ).count()

    return render(request, 'core/predictions.html', {
        'predictions': predictions,
        'next_month':  next_month.strftime('%B %Y'),
        'alert_count': alert_count,
    })


# ── ALERTS ────────────────────────────────────────────
@login_required
def alerts_view(request):
    user = request.user

    alerts = Alert.objects.filter(
        user=user
    ).order_by('-created_at')

    # Mark all as read
    Alert.objects.filter(user=user, is_read=False).update(is_read=True)

    alert_count = 0

    return render(request, 'core/alerts.html', {
        'alerts':      alerts,
        'alert_count': alert_count,
    })


# ── RUN ML PIPELINE ───────────────────────────────────
@login_required
def run_pipeline_view(request):
    user = request.user
    result = run_ml_pipeline(user)
    generate_alerts(user)
    messages.success(
        request,
        f'Pipeline complete! Best model: {result["best_model"]}. '
        f'Predictions updated.'
    )
    return redirect('dashboard')
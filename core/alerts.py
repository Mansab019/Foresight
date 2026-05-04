from core.models import Budget, Prediction, Alert
from django.contrib.auth.models import User
from datetime import date


def generate_alerts(user):
    """
    Compares predictions against budgets
    Creates alert records for any overages
    Returns list of alerts generated
    """

    print(f"\nGenerating alerts for: {user.username}")

    # ── STEP 1: Get current month's budgets ──────────
    today = date.today()
    current_month = today.replace(day=1)

    budgets = Budget.objects.filter(
        user=user,
        month=current_month
    )

    if not budgets.exists():
        print("No budgets set for this month.")
        print("Tip: Add budgets via admin panel first.")
        return []

    # ── STEP 2: Get next month predictions ───────────
    from dateutil.relativedelta import relativedelta
    next_month = current_month + relativedelta(months=1)

    predictions = Prediction.objects.filter(
        user=user,
        prediction_month=next_month
    )

    if not predictions.exists():
        print("No predictions found. Run ML pipeline first.")
        return []

    # Build predictions lookup dict
    # category → predicted_amount
    pred_lookup = {
        p.category: float(p.predicted_amount)
        for p in predictions
    }

    # ── STEP 3: Compare and create alerts ─────────────
    # Clear old unread alerts for this user first
    Alert.objects.filter(user=user, is_read=False).delete()

    alerts_created = []

    for budget in budgets:
        category    = budget.category
        limit       = float(budget.monthly_limit)
        predicted   = pred_lookup.get(category, None)

        if predicted is None:
            print(f"  No prediction found for {category} — skipping")
            continue

        # Calculate overage
        overage = predicted - limit
        overage_pct = (overage / limit) * 100 if limit > 0 else 0

        print(f"\n  {category.upper()}")
        print(f"    Budget:    {limit:,.0f}")
        print(f"    Predicted: {predicted:,.0f}")
        print(f"    Overage:   {overage:,.0f} ({overage_pct:.1f}%)")

        if predicted <= limit:
            print(f"    Status:    ✅ Within budget")
            continue

        # Determine severity
        if overage_pct > 10:
            severity = 'danger'
            emoji = '🔴'
        else:
            severity = 'warning'
            emoji = '🟡'

        # Build alert message
        message = (
            f"{emoji} {category.capitalize()} spending predicted at "
            f"{predicted:,.0f} — exceeds your budget of "
            f"{limit:,.0f} by {overage:,.0f} "
            f"({overage_pct:.1f}% over limit)"
        )

        # Create alert in database
        alert = Alert.objects.create(
            user=user,
            budget=budget,
            message=message,
            severity=severity,
            is_read=False
        )

        alerts_created.append(alert)
        print(f"    Status:    {emoji} {severity.upper()} alert created")

    # ── STEP 4: Summary ───────────────────────────────
    print(f"\nAlerts generated: {len(alerts_created)}")
    danger_count  = sum(1 for a in alerts_created if a.severity == 'danger')
    warning_count = sum(1 for a in alerts_created if a.severity == 'warning')
    print(f"  🔴 Danger:  {danger_count}")
    print(f"  🟡 Warning: {warning_count}")

    return alerts_created
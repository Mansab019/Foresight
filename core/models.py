from django.db import models

# Create your models here.
from django.contrib.auth.models import User


# ─────────────────────────────────────────
# TABLE 1: ImportBatch
# One row per CSV upload — lets us group and
# predict on a single upload's transactions
# separately from the user's full history
# ─────────────────────────────────────────
class ImportBatch(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='import_batches'
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at:%Y-%m-%d %H:%M})"


# ─────────────────────────────────────────
# TABLE 2: Transaction
# Every expense recorded by the user
# ─────────────────────────────────────────
class Transaction(models.Model):

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    SOURCE_CHOICES = [
        ('manual', 'Manual'),
        ('csv', 'CSV Import'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=True,
        blank=True,
        help_text='Set only for rows created via CSV upload — null for manual entries and pre-batch imports'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} | {self.category} | {self.amount}"


# ─────────────────────────────────────────
# TABLE 3: Budget
# Monthly spending limits per category
# ─────────────────────────────────────────
class Budget(models.Model):

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()

    class Meta:
        unique_together = ['user', 'category', 'month']

    def __str__(self):
        return f"{self.user.username} | {self.category} | {self.monthly_limit}"


# ─────────────────────────────────────────
# TABLE 4: Prediction
# ML model output saved here
# ─────────────────────────────────────────
class Prediction(models.Model):

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.CASCADE,
        related_name='predictions',
        null=True,
        blank=True,
        help_text='Set only for predictions generated from a single CSV upload — null for the main merged forecast'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    predicted_amount = models.DecimalField(max_digits=10, decimal_places=2)
    prediction_month = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50, default='v1.0')

    def __str__(self):
        return f"{self.user.username} | {self.category} | {self.predicted_amount}"


# ─────────────────────────────────────────
# TABLE 5: Alert
# Budget breach notifications
# ─────────────────────────────────────────
class Alert(models.Model):

    SEVERITY_CHOICES = [
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.severity} | {self.message[:30]}"
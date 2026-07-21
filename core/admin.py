from django.contrib import admin

# Register your models here.
from .models import Transaction, Budget, Prediction, Alert, ImportBatch

@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'filename', 'row_count', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__username', 'filename']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'category', 'date', 'source', 'batch', 'created_at']
    list_filter = ['category', 'source', 'date']
    search_fields = ['user__username', 'description']
    ordering = ['-date']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'monthly_limit', 'month']
    list_filter = ['category', 'month']
    search_fields = ['user__username']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'predicted_amount', 'prediction_month', 'model_version', 'generated_at']
    list_filter = ['category', 'prediction_month']
    search_fields = ['user__username']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'severity', 'is_read', 'created_at']
    list_filter = ['severity', 'is_read']
    search_fields = ['user__username', 'message']
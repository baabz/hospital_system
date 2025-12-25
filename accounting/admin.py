from django.contrib import admin
from .models import PaymentRecord, ExpenseRecord, DailyCashSummary


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'payment_date', 'amount', 'payment_method', 'payment_type', 'patient', 'received_by']
    list_filter = ['payment_method', 'payment_type', 'payment_date']
    search_fields = ['payment_id', 'patient__first_name', 'patient__last_name', 'reference_number']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'payment_date', 'amount', 'payment_method', 'payment_type')
        }),
        ('References', {
            'fields': ('patient', 'invoice', 'reference_number')
        }),
        ('Additional Details', {
            'fields': ('notes', 'received_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseRecord)
class ExpenseRecordAdmin(admin.ModelAdmin):
    list_display = ['expense_id', 'expense_date', 'amount', 'category', 'payment_method', 'is_approved', 'recorded_by']
    list_filter = ['category', 'payment_method', 'is_approved', 'expense_date']
    search_fields = ['expense_id', 'description', 'vendor', 'receipt_number']
    readonly_fields = ['expense_id', 'created_at', 'updated_at']
    date_hierarchy = 'expense_date'
    actions = ['approve_expenses']
    
    fieldsets = (
        ('Expense Information', {
            'fields': ('expense_id', 'expense_date', 'amount', 'category', 'payment_method')
        }),
        ('Details', {
            'fields': ('description', 'vendor', 'receipt_number', 'receipt_image')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Tracking', {
            'fields': ('recorded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_expenses(self, request, queryset):
        """Bulk approve expenses"""
        for expense in queryset:
            if not expense.is_approved:
                expense.approve(request.user)
        self.message_user(request, f"{queryset.count()} expenses approved successfully.")
    approve_expenses.short_description = "Approve selected expenses"


@admin.register(DailyCashSummary)
class DailyCashSummaryAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_income', 'total_expenses', 'net_amount', 'is_reconciled', 'reconciled_by']
    list_filter = ['is_reconciled', 'date']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    actions = ['calculate_daily_totals']
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Opening Balance', {
            'fields': ('opening_balance',)
        }),
        ('Income', {
            'fields': ('cash_received', 'pos_received', 'bank_transfer_received', 'other_received')
        }),
        ('Expenses', {
            'fields': ('cash_expenses', 'bank_expenses', 'other_expenses')
        }),
        ('Closing Balance', {
            'fields': ('expected_closing_balance', 'actual_closing_balance', 'variance')
        }),
        ('Reconciliation', {
            'fields': ('is_reconciled', 'reconciled_by', 'reconciled_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def calculate_daily_totals(self, request, queryset):
        """Recalculate totals for selected summaries"""
        for summary in queryset:
            summary.calculate_totals()
        self.message_user(request, f"{queryset.count()} summaries recalculated successfully.")
    calculate_daily_totals.short_description = "Recalculate totals for selected summaries"

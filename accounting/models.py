from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
import uuid


def generate_payment_id():
    """Generate unique payment ID"""
    return f"PAY{uuid.uuid4().hex[:8].upper()}"


def generate_expense_id():
    """Generate unique expense ID"""
    return f"EXP{uuid.uuid4().hex[:8].upper()}"


class PaymentRecord(models.Model):
    """Track all incoming payments"""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('POS', 'POS/Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CHEQUE', 'Cheque'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('INVOICE', 'Invoice Payment'),
        ('CONSULTATION', 'Consultation Fee'),
        ('PHARMACY', 'Pharmacy Sale'),
        ('LAB_TEST', 'Lab Test'),
        ('PROCEDURE', 'Medical Procedure'),
        ('OTHER', 'Other Income'),
    ]
    
    payment_id = models.CharField(max_length=20, unique=True, default=generate_payment_id, editable=False)
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # References
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_payments')
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='accounting_payments')
    
    # Payment details
    reference_number = models.CharField(max_length=100, blank=True, help_text="Bank reference, POS receipt number, etc.")
    notes = models.TextField(blank=True)
    
    # Tracking
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payments_received')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounting_payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_date']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['payment_type']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.get_payment_method_display()} - ₦{self.amount}"


class ExpenseRecord(models.Model):
    """Track all expenses"""
    EXPENSE_CATEGORY_CHOICES = [
        ('SALARIES', 'Staff Salaries'),
        ('UTILITIES', 'Utilities (Electricity, Water, etc.)'),
        ('MEDICAL_SUPPLIES', 'Medical Supplies'),
        ('OFFICE_SUPPLIES', 'Office Supplies'),
        ('MAINTENANCE', 'Maintenance & Repairs'),
        ('RENT', 'Rent'),
        ('INSURANCE', 'Insurance'),
        ('LICENSES', 'Licenses & Permits'),
        ('MARKETING', 'Marketing & Advertising'),
        ('TRANSPORT', 'Transport & Fuel'),
        ('FOOD', 'Food & Refreshments'),
        ('EQUIPMENT', 'Equipment Purchase'),
        ('TRAINING', 'Staff Training'),
        ('COMMUNICATION', 'Phone & Internet'),
        ('OTHER', 'Other Expenses'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('DEBIT_CARD', 'Debit Card'),
    ]
    
    expense_id = models.CharField(max_length=20, unique=True, default=generate_expense_id, editable=False)
    expense_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Details
    description = models.TextField()
    vendor = models.CharField(max_length=200, blank=True, help_text="Supplier/Vendor name")
    receipt_number = models.CharField(max_length=100, blank=True)
    receipt_image = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    
    # Approval workflow
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='expenses_recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounting_expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['category']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.expense_id} - {self.get_category_display()} - ₦{self.amount}"
    
    def approve(self, user):
        """Approve this expense"""
        self.is_approved = True
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()


class DailyCashSummary(models.Model):
    """Daily cash reconciliation"""
    date = models.DateField(unique=True)
    
    # Opening balance
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Income by method (auto-calculated from PaymentRecord)
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pos_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_transfer_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Expenses by method (auto-calculated from ExpenseRecord)
    cash_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Closing balance
    expected_closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Reconciliation
    is_reconciled = models.BooleanField(default=False)
    reconciled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounting_daily_summary'
        ordering = ['-date']
        verbose_name_plural = 'Daily Cash Summaries'
    
    def __str__(self):
        return f"Cash Summary - {self.date}"
    
    def calculate_totals(self):
        """Calculate totals from payment and expense records"""
        payments = PaymentRecord.objects.filter(payment_date__date=self.date)
        expenses = ExpenseRecord.objects.filter(expense_date__date=self.date, is_approved=True)
        
        # Calculate income by method
        self.cash_received = payments.filter(payment_method='CASH').aggregate(Sum('amount'))['amount__sum'] or 0
        self.pos_received = payments.filter(payment_method='POS').aggregate(Sum('amount'))['amount__sum'] or 0
        self.bank_transfer_received = payments.filter(payment_method='BANK_TRANSFER').aggregate(Sum('amount'))['amount__sum'] or 0
        self.other_received = payments.filter(payment_method__in=['MOBILE_MONEY', 'CHEQUE']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate expenses by method
        self.cash_expenses = expenses.filter(payment_method='CASH').aggregate(Sum('amount'))['amount__sum'] or 0
        self.bank_expenses = expenses.filter(payment_method='BANK_TRANSFER').aggregate(Sum('amount'))['amount__sum'] or 0
        self.other_expenses = expenses.filter(payment_method__in=['MOBILE_MONEY', 'CHEQUE', 'DEBIT_CARD']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate expected closing balance
        total_income = self.cash_received + self.pos_received + self.bank_transfer_received + self.other_received
        total_expenses = self.cash_expenses + self.bank_expenses + self.other_expenses
        self.expected_closing_balance = self.opening_balance + total_income - total_expenses
        
        # Calculate variance
        self.variance = self.actual_closing_balance - self.expected_closing_balance
        
        self.save()
    
    @property
    def total_income(self):
        return self.cash_received + self.pos_received + self.bank_transfer_received + self.other_received
    
    @property
    def total_expenses(self):
        return self.cash_expenses + self.bank_expenses + self.other_expenses
    
    @property
    def net_amount(self):
        return self.total_income - self.total_expenses

from django.db import models
from django.conf import settings
from patients.models import Patient
from decimal import Decimal
from django.utils import timezone
from accounts.models import User

# Import expense models
from .expenses_models import ExpenseCategory, Expense


class Invoice(models.Model):
    """Patient invoices"""
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            import uuid
            self.invoice_number = f"INV{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_total(self):
        """Calculate invoice total from items and update status"""
        self.subtotal = sum(item.total for item in self.items.all())
        self.total = self.subtotal + self.tax - self.discount
        self.update_payment_status()
        self.save()
    
    def update_payment_status(self):
        """Dynamically update payment status based on amount paid vs total"""
        if self.total == 0:
            self.status = 'unpaid'
        elif self.amount_paid >= self.total:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
    
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total - self.amount_paid


class InvoiceItem(models.Model):
    """Individual line items in an invoice"""
    ITEM_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('procedure', 'Procedure'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('bed_charge', 'Bed Charge'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    class Meta:
        db_table = 'invoice_items'
    
    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        # Recalculate invoice total and status when item changes
        if self.invoice_id:
            self.invoice.calculate_total()
    
    def __str__(self):
        return f"{self.description} - ₦{self.total}"


class Payment(models.Model):
    """Payment records"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('insurance', 'Insurance'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='received_payments')
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment ₦{self.amount} for {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount_paid and recalculate status
        self.invoice.amount_paid = sum(p.amount for p in self.invoice.payments.all())
        self.invoice.update_payment_status()
        self.invoice.save()

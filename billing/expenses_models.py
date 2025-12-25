from django.db import models
from django.utils import timezone
from accounts.models import User


class ExpenseCategory(models.Model):
    """Categories for hospital expenses"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Hospital expenses tracking"""
    EXPENSE_TYPES = [
        ('salary', 'Staff Salary'),
        ('utilities', 'Utilities'),
        ('supplies', 'Medical Supplies'),
        ('equipment', 'Equipment'),
        ('maintenance', 'Maintenance'),
        ('rent', 'Rent'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]
    
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name='expenses')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(default=timezone.now)
    vendor = models.CharField(max_length=200, blank=True, help_text="Supplier or vendor name")
    receipt_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self):
        return f"{self.description} - ₦{self.amount}"

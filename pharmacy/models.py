from django.db import models
from django.conf import settings
from django.utils import timezone


class Medication(models.Model):
    """Pharmacy inventory"""
    CATEGORY_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream/Ointment'),
        ('drops', 'Drops'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    manufacturer = models.CharField(max_length=200, blank=True)
    
    # Inventory
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10, help_text="Alert when stock reaches this level")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Details
    description = models.TextField(blank=True)
    dosage_form = models.CharField(max_length=100, blank=True, help_text="e.g., 500mg, 10ml")
    expiry_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medications'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.dosage_form})"
    
    def is_low_stock(self):
        """Check if medication is low on stock"""
        return self.quantity_in_stock <= self.reorder_level
    
    def is_expired(self):
        """Check if medication is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False


class MedicationDispensing(models.Model):
    """Record of medication dispensing"""
    prescription = models.ForeignKey('medical_records.Prescription', on_delete=models.CASCADE, related_name='dispensing_records')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='dispensing_records')
    
    quantity_dispensed = models.IntegerField()
    dispensed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='medication_dispensing')
    dispensed_at = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'medication_dispensing'
        ordering = ['-dispensed_at']
    
    def __str__(self):
        return f"{self.medication.name} - {self.quantity_dispensed} units"
    
    def save(self, *args, **kwargs):
        # Reduce stock when dispensing
        if not self.pk:  # Only on creation
            self.medication.quantity_in_stock -= self.quantity_dispensed
            self.medication.save()
        super().save(*args, **kwargs)


class StockAdjustment(models.Model):
    """Track stock adjustments (purchases, returns, etc.)"""
    ADJUSTMENT_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('return', 'Return'),
        ('expired', 'Expired'),
        ('damaged', 'Damaged'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPE_CHOICES)
    quantity = models.IntegerField(help_text="Positive for additions, negative for reductions")
    reason = models.TextField()
    
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='stock_adjustments')
    adjusted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_adjustments'
        ordering = ['-adjusted_at']
    
    def __str__(self):
        return f"{self.medication.name} - {self.adjustment_type} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Update medication stock
        if not self.pk:  # Only on creation
            self.medication.quantity_in_stock += self.quantity
            self.medication.save()
        super().save(*args, **kwargs)

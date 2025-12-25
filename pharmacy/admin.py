from django.contrib import admin
from .models import Medication, MedicationDispensing, StockAdjustment


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity_in_stock', 'reorder_level', 'unit_price', 'is_low_stock', 'expiry_date']
    list_filter = ['category', 'expiry_date']
    search_fields = ['name', 'generic_name', 'manufacturer']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'


@admin.register(MedicationDispensing)
class MedicationDispensingAdmin(admin.ModelAdmin):
    list_display = ['medication', 'prescription', 'quantity_dispensed', 'dispensed_by', 'dispensed_at']
    list_filter = ['dispensed_at', 'medication']
    search_fields = ['medication__name', 'prescription__patient__first_name', 'prescription__patient__last_name']
    date_hierarchy = 'dispensed_at'


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['medication', 'adjustment_type', 'quantity', 'adjusted_by', 'adjusted_at']
    list_filter = ['adjustment_type', 'adjusted_at']
    search_fields = ['medication__name']
    date_hierarchy = 'adjusted_at'

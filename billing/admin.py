from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'issue_date', 'total', 'amount_paid', 'balance_due', 'status']
    list_filter = ['status', 'issue_date']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'issue_date'
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'patient', 'issue_date', 'due_date', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax', 'discount', 'total', 'amount_paid')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment_date', 'amount', 'payment_method', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'reference_number']
    date_hierarchy = 'payment_date'

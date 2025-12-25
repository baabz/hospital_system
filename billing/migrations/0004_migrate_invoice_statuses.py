# Generated migration - update invoice statuses

from django.db import migrations


def update_invoice_statuses(apps, schema_editor):
    """Update old status values to new simplified ones"""
    Invoice = apps.get_model('billing', 'Invoice')
    
    # Map old statuses to new ones
    status_mapping = {
        'draft': 'unpaid',
        'issued': 'unpaid',
        'partially_paid': 'partial',
        'paid': 'paid',
        'cancelled': 'unpaid',
    }
    
    for invoice in Invoice.objects.all():
        if invoice.status in status_mapping:
            invoice.status = status_mapping[invoice.status]
            invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_update_invoice_statuses'),
    ]

    operations = [
        migrations.RunPython(update_invoice_statuses, reverse_code=migrations.RunPython.noop),
    ]

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import InvoiceItem


@receiver(post_delete, sender=InvoiceItem)
def recalculate_invoice_on_item_delete(sender, instance, **kwargs):
    """
    Recalculate invoice total and status when an item is deleted
    """
    if instance.invoice_id:
        instance.invoice.calculate_total()

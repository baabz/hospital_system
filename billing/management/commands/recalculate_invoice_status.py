from django.core.management.base import BaseCommand
from billing.models import Invoice


class Command(BaseCommand):
    help = 'Recalculate invoice payment statuses based on amount paid'

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        updated_count = 0

        for invoice in invoices:
            old_status = invoice.status
            
            # Recalculate amount_paid from payments
            invoice.amount_paid = sum(p.amount for p in invoice.payments.all())
            
            # Determine correct status
            if invoice.amount_paid >= invoice.total:
                invoice.status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.status = 'partial'
            else:
                invoice.status = 'unpaid'
            
            # Save if status changed
            if old_status != invoice.status:
                invoice.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {invoice.invoice_number}: {old_status} → {invoice.status} '
                        f'(Paid: ₦{invoice.amount_paid}/{invoice.total}, Balance: ₦{invoice.balance_due()})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully updated {updated_count} invoice(s)')
        )

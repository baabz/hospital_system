from django import forms
from .models import Invoice, InvoiceItem, Payment


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'due_date', 'tax', 'discount', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_type', 'description', 'quantity', 'unit_price']
        widgets = {
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        
        # Add help text showing outstanding balance
        if self.invoice:
            balance = self.invoice.balance_due()
            self.fields['amount'].help_text = f'Outstanding balance: ₦{balance:,.2f}'
            self.fields['amount'].widget.attrs['max'] = str(balance)
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if not self.invoice:
            return amount
        
        # Get current outstanding balance
        outstanding_balance = self.invoice.balance_due()
        
        # Validate payment doesn't exceed balance
        if amount > outstanding_balance:
            raise forms.ValidationError(
                f'Payment amount (₦{amount:,.2f}) cannot exceed outstanding balance (₦{outstanding_balance:,.2f}). '
                f'Please enter an amount up to ₦{outstanding_balance:,.2f}.'
            )
        
        if amount <= 0:
            raise forms.ValidationError('Payment amount must be greater than zero.')
        
        return amount

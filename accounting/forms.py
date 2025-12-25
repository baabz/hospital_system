from django import forms
from .models import PaymentRecord, ExpenseRecord, DailyCashSummary


class PaymentRecordForm(forms.ModelForm):
    """Form for recording payments"""
    class Meta:
        model = PaymentRecord
        fields = [
            'payment_date', 'amount', 'payment_method', 'payment_type',
            'patient', 'invoice', 'reference_number', 'notes'
        ]
        widgets = {
            'payment_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bank ref, POS receipt, etc.'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make invoice and patient optional
        self.fields['invoice'].required = False
        self.fields['patient'].required = False
        self.fields['notes'].required = False


class ExpenseRecordForm(forms.ModelForm):
    """Form for recording expenses"""
    class Meta:
        model = ExpenseRecord
        fields = [
            'expense_date', 'amount', 'category', 'payment_method',
            'description', 'vendor', 'receipt_number', 'receipt_image'
        ]
        widgets = {
            'expense_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the expense...'
            }),
            'vendor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier/Vendor name'
            }),
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Receipt/Invoice number'
            }),
            'receipt_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['vendor'].required = False
        self.fields['receipt_number'].required = False
        self.fields['receipt_image'].required = False


class DailyCashSummaryForm(forms.ModelForm):
    """Form for daily cash reconciliation"""
    class Meta:
        model = DailyCashSummary
        fields = [
            'date', 'opening_balance', 'actual_closing_balance', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'opening_balance': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'actual_closing_balance': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reconciliation notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False


class DateRangeFilterForm(forms.Form):
    """Form for filtering by date range"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    payment_method = forms.ChoiceField(
        required=False,
        choices=[('', 'All Methods')] + PaymentRecord.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

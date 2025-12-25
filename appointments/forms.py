from django import forms
from django.utils import timezone
from .models import Appointment, AppointmentType
from patients.models import Patient
from accounts.models import User


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_type_new', 'appointment_datetime', 'duration_minutes', 'reason', 'status']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_type_new': forms.Select(attrs={
                'class': 'form-control',
                'id': 'appointment-type-select'
            }),
            'appointment_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'doctor': 'Doctor (Optional)',
            'appointment_type_new': 'Appointment Type',
            'appointment_datetime': 'Date & Time',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make doctor field optional
        self.fields['doctor'].required = False
        self.fields['doctor'].queryset = User.objects.filter(role='doctor', is_active_staff=True)
        
        # Filter appointment types to show only active ones
        self.fields['appointment_type_new'].queryset = AppointmentType.objects.filter(is_active=True)
        self.fields['appointment_type_new'].label_from_instance = lambda obj: f"{obj.name} (₦{obj.fee:,.2f})"
    
    def clean_appointment_datetime(self):
        """Validate that appointment datetime is in the future"""
        appointment_datetime = self.cleaned_data.get('appointment_datetime')
        if appointment_datetime and appointment_datetime < timezone.now():
            raise forms.ValidationError("Appointment date and time must be in the future.")
        return appointment_datetime

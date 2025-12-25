from django import forms
from .models import Patient, PatientVisit


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender',
            'blood_group', 'phone', 'email', 'address', 'country', 'state', 'city', 'lga',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'allergies', 'chronic_conditions', 'photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'country': forms.Select(attrs={'class': 'form-control', 'id': 'id_country'}),
            'state': forms.Select(attrs={'class': 'form-control', 'id': 'id_state'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'lga': forms.Select(attrs={'class': 'form-control', 'id': 'id_lga'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import states data from model
        from .models import Patient
        
        # Set initial state choices based on country
        if self.instance and self.instance.pk:
            country = self.instance.country
        else:
            country = self.initial.get('country', 'Nigeria')
        
        # Populate state choices based on country
        if country in Patient.STATES_BY_COUNTRY:
            state_choices = [(state, state) for state in Patient.STATES_BY_COUNTRY[country]]
            self.fields['state'].widget = forms.Select(
                choices=[('', '---------')] + state_choices,
                attrs={'class': 'form-control', 'id': 'id_state'}
            )
        
        # Show/hide LGA field based on country
        if country != 'Nigeria':
            self.fields['lga'].widget = forms.Select(
                attrs={'class': 'form-control', 'id': 'id_lga', 'style': 'display:none;'}
            )
            self.fields['lga'].required = False


class PatientVisitForm(forms.ModelForm):
    class Meta:
        model = PatientVisit
        fields = ['patient', 'reason', 'attending_doctor', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attending_doctor': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

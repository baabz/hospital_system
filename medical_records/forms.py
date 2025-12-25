from django import forms
from .models import Prescription, PrescriptionItem, LabTest, Diagnosis
from patients.models import Patient, PatientVisit
from accounts.models import User


class VitalSignsForm(forms.ModelForm):
    """Form for recording patient vital signs"""
    class Meta:
        model = PatientVisit
        fields = [
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'pulse_rate', 'respiratory_rate', 'weight', 'height', 'oxygen_saturation'
        ]
        widgets = {
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '37.5',
                'step': '0.1',
                'min': '35',
                'max': '42'
            }),
            'blood_pressure_systolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '120',
                'min': '60',
                'max': '250'
            }),
            'blood_pressure_diastolic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '80',
                'min': '40',
                'max': '150'
            }),
            'pulse_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '72',
                'min': '40',
                'max': '200'
            }),
            'respiratory_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '16',
                'min': '8',
                'max': '40'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '70.5',
                'step': '0.1',
                'min': '0'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '175.0',
                'step': '0.1',
                'min': '0'
            }),
            'oxygen_saturation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '98',
                'min': '70',
                'max': '100'
            }),
        }
        labels = {
            'temperature': 'Temperature (°C)',
            'blood_pressure_systolic': 'Blood Pressure - Systolic (mmHg)',
            'blood_pressure_diastolic': 'Blood Pressure - Diastolic (mmHg)',
            'pulse_rate': 'Pulse Rate (bpm)',
            'respiratory_rate': 'Respiratory Rate (breaths/min)',
            'weight': 'Weight (kg)',
            'height': 'Height (cm)',
            'oxygen_saturation': 'Oxygen Saturation (SpO2 %)',
        }


class ClinicalNotesForm(forms.ModelForm):
    """Form for clinical documentation and examination findings"""
    class Meta:
        model = PatientVisit
        fields = [
            'presenting_complaint', 'past_medical_history',
            'examination_findings', 'clinical_notes'
        ]
        widgets = {
            'presenting_complaint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the patient\'s chief complaint and history of presenting illness...'
            }),
            'past_medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Relevant past medical history, previous surgeries, chronic conditions...'
            }),
            'examination_findings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Physical examination findings:\n- General appearance:\n- Cardiovascular:\n- Respiratory:\n- Abdominal:\n- Neurological:\n- Other systems:'
            }),
            'clinical_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Clinical assessment, differential diagnosis, and management plan...'
            }),
        }
        labels = {
            'presenting_complaint': 'Presenting Complaint & History',
            'past_medical_history': 'Past Medical History',
            'examination_findings': 'Physical Examination Findings',
            'clinical_notes': 'Clinical Assessment & Plan',
        }



class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'diagnosis', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure doctor queryset only shows active doctors
        self.fields['doctor'].queryset = User.objects.filter(role='doctor', is_active_staff=True)
        # Doctor field is optional since it can be auto-filled
        self.fields['doctor'].required = False


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medication_name', 'dosage', 'frequency', 'duration', 'quantity', 'instructions']
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 times daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['patient', 'ordered_by', 'test_name', 'test_type', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'ordered_by': forms.Select(attrs={'class': 'form-control'}),
            'test_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Complete Blood Count'}),
            'test_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Blood Test'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordered_by'].queryset = User.objects.filter(role__in=['doctor', 'lab_technician'], is_active_staff=True)


class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['patient', 'doctor', 'diagnosis_code', 'diagnosis_name', 'description', 'treatment_plan', 'follow_up_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ICD-10 code (optional)'}),
            'diagnosis_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='doctor', is_active_staff=True)

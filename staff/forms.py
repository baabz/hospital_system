from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'head']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cardiology'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief description of the department...'}),
            'head': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'name': 'Enter the department name (must be unique)',
            'head': 'Select the department head (optional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter head choices to only show doctors
        from accounts.models import User
        self.fields['head'].queryset = User.objects.filter(role='doctor')
        self.fields['head'].required = False

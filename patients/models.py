from django.db import models
from django.conf import settings
import uuid
from datetime import date


def generate_patient_id():
    """Generate unique patient ID"""
    return f"GAL{uuid.uuid4().hex[:8].upper()}"


class Patient(models.Model):
    """Patient information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    COUNTRY_CHOICES = [
        ('Cameroon', 'Cameroon'),
        ('Senegal', 'Senegal'),
        ('Gabon', 'Gabon'),
        ('Nigeria', 'Nigeria'),
        ('Niger', 'Niger'),
        ('Ghana', 'Ghana'),
    ]
    
    # States/Regions by Country
    STATES_BY_COUNTRY = {
        'Cameroon': [
            'Adamawa', 'Centre', 'East', 'Far North', 'Littoral', 
            'North', 'Northwest', 'South', 'Southwest', 'West'
        ],
        'Senegal': [
            'Dakar', 'Diourbel', 'Fatick', 'Kaffrine', 'Kaolack',
            'Kédougou', 'Kolda', 'Louga', 'Matam', 'Saint-Louis',
            'Sédhiou', 'Tambacounda', 'Thiès', 'Ziguinchor'
        ],
        'Gabon': [
            'Estuaire', 'Haut-Ogooué', 'Moyen-Ogooué', 'Ngounié',
            'Nyanga', 'Ogooué-Ivindo', 'Ogooué-Lolo', 'Ogooué-Maritime',
            'Woleu-Ntem'
        ],
        'Nigeria': [
            'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa',
            'Benue', 'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo',
            'Ekiti', 'Enugu', 'FCT', 'Gombe', 'Imo', 'Jigawa', 'Kaduna',
            'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos', 'Nasarawa',
            'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers',
            'Sokoto', 'Taraba', 'Yobe', 'Zamfara'
        ],
        'Niger': [
            'Agadez', 'Diffa', 'Dosso', 'Maradi', 'Niamey',
            'Tahoua', 'Tillabéri', 'Zinder'
        ],
        'Ghana': [
            'Ahafo', 'Ashanti', 'Bono', 'Bono East', 'Central',
            'Eastern', 'Greater Accra', 'North East', 'Northern',
            'Oti', 'Savannah', 'Upper East', 'Upper West', 'Volta',
            'Western', 'Western North'
        ],
    }
    
    # Adamawa State LGAs (for Nigeria)
    LGA_CHOICES = [
        ('Demsa', 'Demsa'),
        ('Fufore', 'Fufore'),
        ('Ganye', 'Ganye'),
        ('Gayuk', 'Gayuk'),
        ('Gombi', 'Gombi'),
        ('Grie', 'Grie'),
        ('Hong', 'Hong'),
        ('Jada', 'Jada'),
        ('Lamurde', 'Lamurde'),
        ('Madagali', 'Madagali'),
        ('Maiha', 'Maiha'),
        ('Mayo-Belwa', 'Mayo-Belwa'),
        ('Michika', 'Michika'),
        ('Mubi North', 'Mubi North'),
        ('Mubi South', 'Mubi South'),
        ('Numan', 'Numan'),
        ('Shelleng', 'Shelleng'),
        ('Song', 'Song'),
        ('Toungo', 'Toungo'),
        ('Yola North', 'Yola North'),
        ('Yola South', 'Yola South'),
    ]
    
    patient_id = models.CharField(max_length=20, unique=True, default=generate_patient_id, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Contact information
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='Nigeria')
    state = models.CharField(max_length=100, default='Adamawa')
    city = models.CharField(max_length=100, default='Gimeta')
    lga = models.CharField(max_length=100, choices=LGA_CHOICES, blank=True, verbose_name='LGA', help_text='Local Government Area (Nigeria only)')
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_phone = models.CharField(max_length=15)
    emergency_contact_relationship = models.CharField(max_length=50)
    
    # Medical information
    allergies = models.TextField(blank=True, help_text="List any known allergies")
    chronic_conditions = models.TextField(blank=True, help_text="List any chronic conditions")
    
    # Photo
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    
    # Metadata
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        middle = f" {self.middle_name}" if self.middle_name else ""
        return f"{self.first_name}{middle} {self.last_name}"
    
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class PatientVisit(models.Model):
    """Enhanced patient visit with comprehensive clinical documentation"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateTimeField(auto_now_add=True)
    attending_doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='patient_visits')
    
    # Reason for visit
    reason = models.TextField(help_text="Chief complaint/reason for visit")
    
    # Vital Signs - Structured fields for proper medical documentation
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True, 
        help_text="Body temperature in °C (e.g., 37.5)"
    )
    blood_pressure_systolic = models.IntegerField(
        null=True, blank=True, 
        help_text="Systolic BP in mmHg (e.g., 120)"
    )
    blood_pressure_diastolic = models.IntegerField(
        null=True, blank=True, 
        help_text="Diastolic BP in mmHg (e.g., 80)"
    )
    pulse_rate = models.IntegerField(
        null=True, blank=True, 
        help_text="Heart rate in beats per minute (e.g., 72)"
    )
    respiratory_rate = models.IntegerField(
        null=True, blank=True, 
        help_text="Breaths per minute (e.g., 16)"
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, 
        help_text="Weight in kg (e.g., 70.5)"
    )
    height = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, 
        help_text="Height in cm (e.g., 175.0)"
    )
    oxygen_saturation = models.IntegerField(
        null=True, blank=True, 
        help_text="SpO2 percentage (e.g., 98)"
    )
    
    # Clinical Documentation
    presenting_complaint = models.TextField(
        blank=True, 
        help_text="Detailed history of presenting illness"
    )
    past_medical_history = models.TextField(
        blank=True, 
        help_text="Relevant past medical history for this visit"
    )
    examination_findings = models.TextField(
        blank=True, 
        help_text="Physical examination findings (inspection, palpation, percussion, auscultation)"
    )
    clinical_notes = models.TextField(
        blank=True, 
        help_text="Doctor's clinical assessment, differential diagnosis, and plan"
    )
    
    # Legacy fields (kept for backward compatibility)
    vital_signs = models.JSONField(blank=True, null=True, help_text="Legacy vital signs storage")
    notes = models.TextField(blank=True, help_text="Legacy general notes field")
    
    class Meta:
        db_table = 'patient_visits'
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
    
    def get_blood_pressure(self):
        """Return formatted blood pressure string"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None
    
    def get_bmi(self):
        """Calculate and return BMI if weight and height are available"""
        if self.weight and self.height:
            height_m = self.height / 100  # Convert cm to meters
            bmi = self.weight / (height_m ** 2)
            return round(bmi, 1)
        return None
    
    def has_vital_signs(self):
        """Check if any vital signs have been recorded"""
        return any([
            self.temperature,
            self.blood_pressure_systolic,
            self.pulse_rate,
            self.respiratory_rate,
            self.weight,
            self.oxygen_saturation
        ])
    
    def has_clinical_notes(self):
        """Check if clinical documentation has been completed"""
        return any([
            self.presenting_complaint,
            self.examination_findings,
            self.clinical_notes
        ])

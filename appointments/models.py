from django.db import models
from django.conf import settings
from patients.models import Patient


class AppointmentType(models.Model):
    """Appointment types with configurable fees"""
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Consultation')")
    code = models.CharField(max_length=50, unique=True, help_text="Unique code (e.g., 'consultation')")
    fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fee amount in Naira")
    description = models.TextField(blank=True, help_text="Optional description of this appointment type")
    is_active = models.BooleanField(default=True, help_text="Whether this type is available for booking")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointment_types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (₦{self.fee:,.2f})"

class Appointment(models.Model):
    """Patient appointments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Keep old TYPE_CHOICES for migration reference
    TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('checkup', 'Check-up'),
        ('procedure', 'Procedure'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    # Doctor is now optional - will be assigned after session completion
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_appointments',
        null=True,
        blank=True,
        help_text="Doctor will be assigned after completing the session"
    )
    
    # New ForeignKey to AppointmentType (will replace old CharField)
    appointment_type_new = models.ForeignKey(
        AppointmentType,
        on_delete=models.PROTECT,
        related_name='appointments',
        null=True,
        blank=True,
        help_text="Type of appointment"
    )
    
    # Keep old field temporarily for migration
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='consultation')
    
    # New datetime field (will replace separate date/time)
    appointment_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time of appointment"
    )
    
    # Keep old fields temporarily for migration
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    duration_minutes = models.IntegerField(default=30)
    
    # Fee field - auto-populated from AppointmentType
    fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Appointment fee (auto-populated from appointment type)"
    )
    
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Link to patient visit (created when consultation starts)
    visit = models.OneToOneField(
        'patients.PatientVisit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
        help_text="Patient visit record created when consultation starts"
    )
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'doctor']),
            models.Index(fields=['patient', 'appointment_date']),
        ]
    
    def __str__(self):
        doctor_name = self.doctor.get_full_name() if self.doctor else "Unassigned"
        # Use new datetime field if available, otherwise fall back to old fields
        if self.appointment_datetime:
            return f"{self.patient.get_full_name()} - {doctor_name} on {self.appointment_datetime.strftime('%Y-%m-%d at %H:%M')}"
        return f"{self.patient.get_full_name()} - {doctor_name} on {self.appointment_date} at {self.appointment_time}"
    
    def save(self, *args, **kwargs):
        # Auto-populate fee from appointment_type_new if not already set
        if self.appointment_type_new and not self.fee:
            self.fee = self.appointment_type_new.fee
        # Backfill legacy date/time fields from appointment_datetime when provided
        if self.appointment_datetime:
            try:
                self.appointment_date = self.appointment_datetime.date()
                self.appointment_time = self.appointment_datetime.time()
            except Exception:
                pass
        super().save(*args, **kwargs)
    
    def start_consultation(self, doctor=None):
        """
        Start consultation - creates a visit record and updates status to confirmed.
        Returns the created PatientVisit object.
        """
        from patients.models import PatientVisit
        from django.utils import timezone
        
        if self.visit:
            # Consultation already started
            return self.visit
        
        # Use provided doctor or appointment's assigned doctor
        attending_doctor = doctor or self.doctor
        
        # Create visit record
        visit = PatientVisit.objects.create(
            patient=self.patient,
            reason=self.reason,
            attending_doctor=attending_doctor
        )
        
        # Link visit to appointment and update status
        self.visit = visit
        self.status = 'confirmed'
        
        # Assign doctor if not already assigned
        if not self.doctor and attending_doctor:
            self.doctor = attending_doctor
        
        self.save()
        return visit
    
    def complete_consultation(self):
        """
        Mark consultation as completed.
        """
        self.status = 'completed'
        self.save()
    
    def can_start_consultation(self):
        """Check if consultation can be started"""
        return self.status == 'pending' and not self.visit
    
    def can_complete(self):
        """Check if appointment can be manually completed"""
        return self.status in ['pending', 'confirmed'] and self.visit


class AppointmentReminder(models.Model):
    """Track appointment reminders sent"""
    REMINDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField(help_text="When the reminder should be sent")
    status = models.CharField(max_length=20, choices=REMINDER_STATUS_CHOICES, default='pending')
    reminder_type = models.CharField(max_length=20, choices=[('email', 'Email')], default='email')

    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointment_reminders'
        ordering = ['reminder_time']
        indexes = [
            models.Index(fields=['status', 'reminder_time']),
        ]

    def __str__(self):
        return f"Reminder for {self.appointment.patient.get_full_name()} - {self.reminder_time.strftime('%Y-%m-%d %H:%M')}"


class ReminderSettings(models.Model):
    """Global reminder settings"""
    hours_before = models.IntegerField(
        default=24,
        help_text="Hours before appointment to send reminder (e.g., 24 means remind 1 day before)"
    )
    is_enabled = models.BooleanField(default=True, help_text="Enable/disable all reminders")
    send_email = models.BooleanField(default=True, help_text="Send email reminders")

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reminder_settings'
        verbose_name_plural = "Reminder Settings"

    def __str__(self):
        return f"Send reminders {self.hours_before} hours before appointment"

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings object"""
        settings_obj, created = cls.objects.get_or_create(pk=1)
        return settings_obj

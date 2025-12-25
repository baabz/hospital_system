from django.db import models
from django.conf import settings
from patients.models import Patient


class Prescription(models.Model):
    """Doctor prescriptions"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    visit = models.ForeignKey('patients.PatientVisit', on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    
    diagnosis = models.TextField()
    prescription_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # Dispensing status
    is_dispensed = models.BooleanField(default=False)
    dispensed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispensed_prescriptions')
    dispensed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescription_date']
    
    def __str__(self):
        return f"Prescription for {self.patient.get_full_name()} - {self.prescription_date.strftime('%Y-%m-%d')}"


class PrescriptionItem(models.Model):
    """Individual medication items in a prescription"""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g., 3 times daily")
    duration = models.CharField(max_length=100, help_text="e.g., 7 days")
    quantity = models.IntegerField(help_text="Total quantity to dispense")
    instructions = models.TextField(blank=True, help_text="Special instructions")
    
    class Meta:
        db_table = 'prescription_items'
    
    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"


class LabTest(models.Model):
    """Laboratory test orders and results"""
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_tests')
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordered_lab_tests')
    visit = models.ForeignKey('patients.PatientVisit', on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_tests')
    
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=100, help_text="e.g., Blood Test, X-Ray, MRI")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    
    ordered_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    results = models.TextField(blank=True)
    result_file = models.FileField(upload_to='lab_results/', blank=True, null=True)
    
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='conducted_lab_tests')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'lab_tests'
        ordering = ['-ordered_at']
    
    def __str__(self):
        return f"{self.test_name} for {self.patient.get_full_name()}"


class Diagnosis(models.Model):
    """Patient diagnoses"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diagnoses')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnoses')
    visit = models.ForeignKey('patients.PatientVisit', on_delete=models.SET_NULL, null=True, blank=True, related_name='diagnoses')
    
    diagnosis_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code if applicable")
    diagnosis_name = models.CharField(max_length=200)
    description = models.TextField()
    treatment_plan = models.TextField()
    
    diagnosed_at = models.DateTimeField(auto_now_add=True)
    follow_up_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'diagnoses'
        ordering = ['-diagnosed_at']
        verbose_name_plural = 'Diagnoses'
    
    def __str__(self):
        return f"{self.diagnosis_name} - {self.patient.get_full_name()}"

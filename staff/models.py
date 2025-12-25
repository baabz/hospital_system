from django.db import models
from django.conf import settings
import uuid


class Department(models.Model):
    """Hospital departments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StaffSchedule(models.Model):
    """Staff duty roster"""
    SHIFT_CHOICES = [
        ('morning', 'Morning (6AM - 2PM)'),
        ('afternoon', 'Afternoon (2PM - 10PM)'),
        ('night', 'Night (10PM - 6AM)'),
    ]
    
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'staff_schedules'
        ordering = ['-date', 'shift']
        unique_together = ['staff', 'date', 'shift']
    
    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.date} ({self.get_shift_display()})"


class Ward(models.Model):
    """Hospital wards"""
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='wards')
    capacity = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'wards'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"
    
    def available_beds(self):
        occupied = self.beds.filter(is_occupied=True).count()
        return self.capacity - occupied


class Bed(models.Model):
    """Hospital beds"""
    bed_number = models.CharField(max_length=20)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    is_occupied = models.BooleanField(default=False)
    current_patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bed')
    
    class Meta:
        db_table = 'beds'
        ordering = ['ward', 'bed_number']
        unique_together = ['ward', 'bed_number']
    
    def __str__(self):
        return f"{self.ward.name} - Bed {self.bed_number}"

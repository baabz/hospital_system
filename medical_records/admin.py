from django.contrib import admin
from .models import Prescription, PrescriptionItem, LabTest, Diagnosis


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'prescription_date', 'is_dispensed']
    list_filter = ['is_dispensed', 'prescription_date', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'prescription_date'
    inlines = [PrescriptionItemInline]
    
    fieldsets = (
        ('Prescription Details', {
            'fields': ('patient', 'doctor', 'visit', 'diagnosis')
        }),
        ('Dispensing Information', {
            'fields': ('is_dispensed', 'dispensed_by', 'dispensed_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    readonly_fields = ['prescription_date']


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'test_name', 'test_type', 'status', 'ordered_at', 'completed_at']
    list_filter = ['status', 'test_type', 'ordered_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id', 'test_name']
    date_hierarchy = 'ordered_at'


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['patient', 'diagnosis_name', 'doctor', 'diagnosed_at', 'follow_up_date']
    list_filter = ['diagnosed_at', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis_name', 'diagnosis_code']
    date_hierarchy = 'diagnosed_at'

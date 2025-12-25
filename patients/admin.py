from django.contrib import admin
from .models import Patient, PatientVisit


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'get_full_name', 'phone', 'gender', 'blood_group', 'created_at']
    list_filter = ['gender', 'blood_group', 'state', 'created_at']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone', 'email']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('patient_id', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'blood_group', 'photo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'city', 'state')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Medical Information', {
            'fields': ('allergies', 'chronic_conditions')
        }),
        ('Metadata', {
            'fields': ('registered_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(PatientVisit)
class PatientVisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'visit_date', 'attending_doctor', 'reason']
    list_filter = ['visit_date', 'attending_doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    date_hierarchy = 'visit_date'

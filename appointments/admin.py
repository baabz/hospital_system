from django.contrib import admin
from .models import Appointment, AppointmentType


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'fee', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    list_editable = ['fee', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('Fee Configuration', {
            'fields': ('fee', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_datetime_display', 'status', 'appointment_type_display', 'fee']
    list_filter = ['status', 'appointment_type_new', 'doctor']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id', 'doctor__first_name', 'doctor__last_name']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'appointment_type_new', 'appointment_datetime', 'duration_minutes', 'fee')
        }),
        ('Information', {
            'fields': ('reason', 'status', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'fee']
    
    def appointment_datetime_display(self, obj):
        """Display datetime in a readable format"""
        if obj.appointment_datetime:
            return obj.appointment_datetime.strftime('%Y-%m-%d %H:%M')
        return f"{obj.appointment_date} {obj.appointment_time}"
    appointment_datetime_display.short_description = 'Date & Time'
    
    def appointment_type_display(self, obj):
        """Display appointment type"""
        if obj.appointment_type_new:
            return obj.appointment_type_new.name
        return obj.appointment_type
    appointment_type_display.short_description = 'Type'

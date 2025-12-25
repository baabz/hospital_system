from django.contrib import admin
from .models import Department, StaffSchedule, Ward, Bed


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'created_at']
    search_fields = ['name']


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'date', 'shift']
    list_filter = ['shift', 'date']
    search_fields = ['staff__first_name', 'staff__last_name']
    date_hierarchy = 'date'


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'capacity', 'available_beds']
    list_filter = ['department']
    search_fields = ['name']


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'ward', 'is_occupied', 'current_patient']
    list_filter = ['is_occupied', 'ward']
    search_fields = ['bed_number', 'ward__name']

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum, F
from django.db import models
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient, PatientVisit
from appointments.models import Appointment
from billing.models import Invoice, Payment
from pharmacy.models import Medication


def index(request):
    """Landing page - redirect to dashboard if logged in"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Main dashboard with statistics"""
    today = timezone.now().date()
    
    # Patient statistics
    total_patients = Patient.objects.count()
    new_patients_this_month = Patient.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Appointment statistics
    todays_appointments = Appointment.objects.filter(appointment_date=today).count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    
    # Billing statistics
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_invoices = Invoice.objects.filter(status__in=['issued', 'partially_paid']).count()
    
    # Pharmacy alerts
    low_stock_medications = Medication.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).count()
    
    # Recent activities
    recent_visits = PatientVisit.objects.select_related('patient', 'attending_doctor')[:5]
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today
    ).select_related('patient', 'doctor').order_by('appointment_date', 'appointment_time')[:5]
    
    context = {
        'total_patients': total_patients,
        'new_patients_this_month': new_patients_this_month,
        'todays_appointments': todays_appointments,
        'pending_appointments': pending_appointments,
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'low_stock_medications': low_stock_medications,
        'recent_visits': recent_visits,
        'upcoming_appointments': upcoming_appointments,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

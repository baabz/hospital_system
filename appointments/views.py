from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm


@login_required
def appointment_list(request):
    """List all appointments"""
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    
    appointments = appointments.order_by('appointment_date', 'appointment_time')
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'today': timezone.now().date(),
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_create(request):
    """Create new appointment"""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.created_by = request.user
            
            # Auto-populate fee from appointment_type_new if available
            if appointment.appointment_type_new:
                appointment.fee = appointment.appointment_type_new.fee
            
            appointment.save()
            
            patient_name = appointment.patient.get_full_name()
            if appointment.doctor:
                messages.success(request, f'Appointment booked successfully for {patient_name} with Dr. {appointment.doctor.get_full_name()}!')
            else:
                messages.success(request, f'Appointment booked successfully for {patient_name}. Doctor will be assigned later.')
            
            return redirect('appointments:appointment_list')
        else:
            # Debug: Log validation errors
            print("=" * 50)
            print("FORM VALIDATION FAILED")
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
            print("=" * 50)
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill patient if passed via query param (link from patient detail)
        patient_pk = request.GET.get('patient')
        if patient_pk:
            form = AppointmentForm(initial={'patient': patient_pk})
        else:
            form = AppointmentForm()
    
    context = {'form': form}
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_update(request, pk):
    """Update appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'is_update': True,
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_delete(request, pk):
    """Delete appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        patient_name = appointment.patient.get_full_name()
        appointment.delete()
        messages.success(request, f'Appointment for {patient_name} cancelled successfully!')
        return redirect('appointments:appointment_list')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_confirm_delete.html', context)


@login_required
def appointment_calendar(request):
    """Calendar view of appointments"""
    # Get current month or requested month
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Get appointments for the month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    appointments = Appointment.objects.filter(
        appointment_date__gte=start_date,
        appointment_date__lt=end_date
    ).select_related('patient', 'doctor')
    
    context = {
        'appointments': appointments,
        'year': year,
        'month': month,
        'today': timezone.now().date(),
    }
    return render(request, 'appointments/appointment_calendar.html', context)


@login_required
def appointment_start_consultation(request, pk):
    """Start consultation - creates visit and updates status"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if not appointment.can_start_consultation():
        messages.warning(request, 'This consultation has already been started or cannot be started.')
        return redirect('appointments:appointment_list')
    
    # Start consultation (creates visit record)
    visit = appointment.start_consultation(doctor=request.user if request.user.role == 'doctor' else None)
    
    messages.success(
        request, 
        f'Consultation started for {appointment.patient.get_full_name()}. You can now create prescriptions and diagnoses.'
    )
    
    # Redirect to prescription form with appointment context
    return redirect('medical_records:prescription_create_from_appointment', appointment_id=pk)


@login_required
def appointment_complete(request, pk):
    """Manually complete an appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        if appointment.can_complete():
            appointment.complete_consultation()
            messages.success(request, f'Appointment for {appointment.patient.get_full_name()} marked as completed.')
        else:
            messages.warning(request, 'This appointment cannot be completed.')
        
        return redirect('appointments:appointment_list')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/appointment_confirm_complete.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Patient, PatientVisit
from .forms import PatientForm, PatientVisitForm


@login_required
def patient_list(request):
    """List all patients with search functionality"""
    query = request.GET.get('q', '')
    
    patients = Patient.objects.all()
    
    if query:
        patients = patients.filter(
            Q(patient_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )
    
    patients = patients.order_by('-created_at')
    
    context = {
        'patients': patients,
        'query': query,
    }
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, patient_id):
    """View patient details and medical history"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    visits = patient.visits.all().order_by('-visit_date')[:10]
    appointments = patient.appointments.all().order_by('-appointment_date')[:10]
    prescriptions = patient.prescriptions.all().order_by('-prescription_date')[:10]
    invoices = patient.invoices.all().order_by('-created_at')[:10]
    
    context = {
        'patient': patient,
        'visits': visits,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'invoices': invoices,
    }
    return render(request, 'patients/patient_detail.html', context)


@login_required
def patient_create(request):
    """Register a new patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.save()
            messages.success(request, f'Patient {patient.get_full_name()} registered successfully! ID: {patient.patient_id}')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm()
    
    context = {'form': form}
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_update(request, patient_id):
    """Update patient information"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient {patient.get_full_name()} updated successfully!')
            return redirect('patients:patient_detail', patient_id=patient.patient_id)
    else:
        form = PatientForm(instance=patient)
    
    context = {
        'form': form,
        'patient': patient,
        'is_update': True,
    }
    return render(request, 'patients/patient_form.html', context)


@login_required
def patient_delete(request, patient_id):
    """Delete a patient"""
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        patient_name = patient.get_full_name()
        patient.delete()
        messages.success(request, f'Patient {patient_name} deleted successfully!')
        return redirect('patients:patient_list')
    
    context = {'patient': patient}
    return render(request, 'patients/patient_confirm_delete.html', context)


@login_required
def patient_search_api(request):
    """API endpoint for patient search - returns JSON results"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search patients by ID, name, phone, email
    patients = Patient.objects.filter(
        Q(patient_id__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(email__icontains=query)
    ).values(
        'patient_id', 'first_name', 'last_name', 'phone', 'gender', 'date_of_birth'
    )[:10]  # Limit to 10 results
    
    results = []
    for patient in patients:
        full_name = f"{patient['first_name']} {patient['last_name']}"
        # Compute age from date_of_birth if available
        dob = patient.get('date_of_birth')
        age = 'N/A'
        if dob:
            try:
                # date_of_birth is a date string from values(); parse if needed
                if isinstance(dob, str):
                    from datetime import datetime as _dt
                    dob_dt = _dt.fromisoformat(dob)
                else:
                    dob_dt = dob
                from datetime import date as _date
                today = _date.today()
                age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
            except Exception:
                age = 'N/A'
        results.append({
            'id': patient['patient_id'],
            'name': full_name,
            'patient_id': patient['patient_id'],
            'phone': patient['phone'],
            'gender': patient['gender'],
            'age': age,
        })
    
    return JsonResponse({'results': results})

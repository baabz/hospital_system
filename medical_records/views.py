from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Prescription, PrescriptionItem, LabTest, Diagnosis
from patients.models import Patient, PatientVisit
from .forms import (PrescriptionForm, PrescriptionItemForm, LabTestForm, DiagnosisForm,
                    VitalSignsForm, ClinicalNotesForm)
from django.utils import timezone


@login_required
def prescription_list(request):
    """List all prescriptions"""
    prescriptions = Prescription.objects.select_related('patient', 'doctor').order_by('-prescription_date')
    context = {'prescriptions': prescriptions}
    return render(request, 'medical_records/prescription_list.html', context)


@login_required
def prescription_create(request, patient_id=None, appointment_id=None):
    """Create new prescription"""
    patient = None
    appointment = None
    
    if patient_id:
        patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if appointment_id:
        from appointments.models import Appointment
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        patient = appointment.patient
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            # Auto-set doctor if current user is a doctor and not already set
            if request.user.role == 'doctor' and not prescription.doctor:
                prescription.doctor = request.user
            
            # Link to appointment's visit if coming from appointment
            if appointment and appointment.visit:
                prescription.visit = appointment.visit
            
            prescription.save()
            
            # Auto-complete the appointment when prescription is created
            if appointment and appointment.status != 'completed':
                appointment.complete_consultation()
            
            messages.success(request, f'Prescription created for {prescription.patient.get_full_name()}!')
            return redirect('medical_records:prescription_detail', pk=prescription.pk)
    else:
        initial = {}
        if patient:
            initial['patient'] = patient.pk
        if request.user.role == 'doctor':
            initial['doctor'] = request.user.pk
        form = PrescriptionForm(initial=initial)
    
    context = {
        'form': form,
        'patient': patient,
        'appointment': appointment,
    }
    return render(request, 'medical_records/prescription_form.html', context)


@login_required
def prescription_detail(request, pk):
    """View prescription details"""
    prescription = get_object_or_404(Prescription, pk=pk)
    context = {'prescription': prescription}
    return render(request, 'medical_records/prescription_detail.html', context)


@login_required
def prescription_item_create(request, prescription_id):
    """Add medication item to prescription"""
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.prescription = prescription
            item.save()
            messages.success(request, 'Medication added to prescription!')
            return redirect('medical_records:prescription_detail', pk=prescription.pk)
    else:
        form = PrescriptionItemForm()
    
    context = {
        'form': form,
        'prescription': prescription,
    }
    return render(request, 'medical_records/prescription_item_form.html', context)


# Lab Tests
@login_required
def lab_test_list(request):
    """List all lab tests"""
    lab_tests = LabTest.objects.select_related('patient', 'ordered_by').order_by('-ordered_at')
    context = {'lab_tests': lab_tests}
    return render(request, 'medical_records/lab_test_list.html', context)


@login_required
def lab_test_create(request, patient_id=None):
    """Create new lab test order"""
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = LabTestForm(request.POST)
        if form.is_valid():
            lab_test = form.save()
            messages.success(request, f'Lab test ordered for {lab_test.patient.get_full_name()}!')
            return redirect('patients:patient_detail', patient_id=lab_test.patient.patient_id)
    else:
        initial = {}
        if patient:
            initial['patient'] = patient.pk
        if request.user.role in ['doctor', 'lab_technician']:
            initial['ordered_by'] = request.user.pk
        form = LabTestForm(initial=initial)
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/lab_test_form.html', context)


@login_required
def lab_test_detail(request, pk):
    """View lab test details"""
    lab_test = get_object_or_404(LabTest, pk=pk)
    context = {'lab_test': lab_test}
    return render(request, 'medical_records/lab_test_detail.html', context)


@login_required
def lab_test_update(request, pk):
    """Update lab test results"""
    lab_test = get_object_or_404(LabTest, pk=pk)
    
    if request.method == 'POST':
        form = LabTestForm(request.POST, request.FILES, instance=lab_test)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lab test updated!')
            return redirect('medical_records:lab_test_detail', pk=lab_test.pk)
    else:
        form = LabTestForm(instance=lab_test)
    
    context = {
        'form': form,
        'lab_test': lab_test,
    }
    return render(request, 'medical_records/lab_test_form.html', context)


# Diagnoses
@login_required
def diagnosis_list(request):
    """List all diagnoses"""
    diagnoses = Diagnosis.objects.select_related('patient', 'doctor').order_by('-diagnosed_at')
    context = {'diagnoses': diagnoses}
    return render(request, 'medical_records/diagnosis_list.html', context)


@login_required
def diagnosis_create(request, patient_id=None):
    """Create new diagnosis"""
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, patient_id=patient_id)
    
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            diagnosis = form.save()
            messages.success(request, f'Diagnosis recorded for {diagnosis.patient.get_full_name()}!')
            return redirect('patients:patient_detail', patient_id=diagnosis.patient.patient_id)
    else:
        initial = {}
        if patient:
            initial['patient'] = patient.pk
        if request.user.role == 'doctor':
            initial['doctor'] = request.user.pk
        form = DiagnosisForm(initial=initial)
    
    context = {
        'form': form,
        'patient': patient,
    }
    return render(request, 'medical_records/diagnosis_form.html', context)


# Vital Signs and Clinical Documentation
@login_required
def vital_signs_update(request, visit_id):
    """Record or update vital signs for a patient visit"""
    visit = get_object_or_404(PatientVisit, pk=visit_id)
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vital signs recorded successfully!')
            # Redirect to clinical notes if not yet completed
            if not visit.has_clinical_notes():
                return redirect('medical_records:clinical_notes_update', visit_id=visit.pk)
            return redirect('patients:patient_detail', patient_id=visit.patient.patient_id)
    else:
        form = VitalSignsForm(instance=visit)
    
    context = {
        'form': form,
        'visit': visit,
    }
    return render(request, 'medical_records/vital_signs_form.html', context)


@login_required
def clinical_notes_update(request, visit_id):
    """Record or update clinical documentation for a patient visit"""
    visit = get_object_or_404(PatientVisit, pk=visit_id)
    
    if request.method == 'POST':
        form = ClinicalNotesForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Clinical documentation saved successfully!')
            # Redirect to patient detail or prescription creation
            return redirect('patients:patient_detail', patient_id=visit.patient.patient_id)
    else:
        form = ClinicalNotesForm(instance=visit)
    
    context = {
        'form': form,
        'visit': visit,
    }
    return render(request, 'medical_records/clinical_notes_form.html', context)


# NEW: Multi-Step Prescription Wizard
@login_required
def prescription_wizard(request, patient_id, step=1):
    """
    Multi-step prescription wizard for complete clinical documentation
    Step 1: Vital Signs
    Step 2: Clinical Assessment
    Step 3: Diagnosis
    Step 4: Prescription
    """
    patient = get_object_or_404(Patient, patient_id=patient_id)
    
    # Get or create visit for this wizard session
    wizard_data = request.session.get('prescription_wizard', {})
    
    if wizard_data.get('patient_id') != patient_id:
        # New wizard session - create visit
        visit = PatientVisit.objects.create(
            patient=patient,
            attending_doctor=request.user if request.user.role == 'doctor' else None,
            reason='Clinical consultation',
            visit_date=timezone.now()
        )
        wizard_data = {
            'patient_id': patient_id,
            'visit_id': visit.pk,
            'current_step': 1,
            'completed_steps': [],
        }
        request.session['prescription_wizard'] = wizard_data
    else:
        visit = get_object_or_404(PatientVisit, pk=wizard_data['visit_id'])
    
    # Handle form submission
    if request.method == 'POST':
        if step == 1:
            form = VitalSignsForm(request.POST, instance=visit)
            if form.is_valid():
                form.save()
                wizard_data['completed_steps'] = list(set(wizard_data.get('completed_steps', []) + [1]))
                wizard_data['current_step'] = 2
                request.session['prescription_wizard'] = wizard_data
                messages.success(request, 'Vital signs recorded!')
                return redirect('medical_records:prescription_wizard_step', patient_id=patient_id, step=2)
        
        elif step == 2:
            form = ClinicalNotesForm(request.POST, instance=visit)
            if form.is_valid():
                form.save()
                wizard_data['completed_steps'] = list(set(wizard_data.get('completed_steps', []) + [2]))
                wizard_data['current_step'] = 3
                request.session['prescription_wizard'] = wizard_data
                messages.success(request, 'Clinical assessment saved!')
                return redirect('medical_records:prescription_wizard_step', patient_id=patient_id, step=3)
        
        elif step == 3:
            form = DiagnosisForm(request.POST)
            if form.is_valid():
                diagnosis = form.save(commit=False)
                diagnosis.visit = visit
                diagnosis.save()
                wizard_data['completed_steps'] = list(set(wizard_data.get('completed_steps', []) + [3]))
                wizard_data['current_step'] = 4
                wizard_data['diagnosis_id'] = diagnosis.pk
                request.session['prescription_wizard'] = wizard_data
                messages.success(request, 'Diagnosis recorded!')
                return redirect('medical_records:prescription_wizard_step', patient_id=patient_id, step=4)
        
        elif step == 4:
            form = PrescriptionForm(request.POST)
            if form.is_valid():
                prescription = form.save(commit=False)
                prescription.visit = visit
                prescription.save()
                # Clear wizard session
                if 'prescription_wizard' in request.session:
                    del request.session['prescription_wizard']
                messages.success(request, 'Prescription created successfully! Clinical documentation complete.')
                return redirect('medical_records:prescription_detail', pk=prescription.pk)
    
    # Prepare form for current step
    if step == 1:
        form = VitalSignsForm(instance=visit)
        template = 'medical_records/wizard/step1_vital_signs.html'
    elif step == 2:
        form = ClinicalNotesForm(instance=visit)
        template = 'medical_records/wizard/step2_clinical_notes.html'
    elif step == 3:
        initial = {'patient': patient.pk, 'doctor': request.user.pk if request.user.role == 'doctor' else None}
        form = DiagnosisForm(initial=initial)
        template = 'medical_records/wizard/step3_diagnosis.html'
    elif step == 4:
        initial = {'patient': patient.pk, 'doctor': request.user.pk if request.user.role == 'doctor' else None}
        form = PrescriptionForm(initial=initial)
        template = 'medical_records/wizard/step4_prescription.html'
    else:
        return redirect('medical_records:prescription_wizard', patient_id=patient_id)
    
    context = {
        'patient': patient,
        'visit': visit,
        'form': form,
        'current_step': step,
        'total_steps': 4,
        'completed_steps': wizard_data.get('completed_steps', []),
        'wizard_data': wizard_data,
    }
    
    return render(request, template, context)

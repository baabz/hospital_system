import os
import django
from datetime import date, datetime, timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galbose.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from decimal import Decimal

from patients.models import Patient
from appointments.models import Appointment, AppointmentType, AppointmentReminder, ReminderSettings
from medical_records.models import Prescription, PrescriptionItem


User = get_user_model()


def run():
    print('Starting smoke test...')

    # Create or get a doctor user
    doctor, created = User.objects.get_or_create(username='smoke_doctor', defaults={
        'first_name': 'Smoke',
        'last_name': 'Doctor',
        'email': 'smoke.doctor@example.test',
    })
    if created:
        doctor.set_password('testpass123')
        doctor.role = 'doctor'
        doctor.save()
        print('Created doctor user')
    else:
        print('Using existing doctor user')

    # Create a patient
    patient, _ = Patient.objects.get_or_create(
        phone='08000000000',
        defaults={
            'first_name': 'Test',
            'last_name': 'Patient',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'M',
            'address': '123 Test St',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '08100000000',
            'emergency_contact_relationship': 'Sibling',
            'registered_by': doctor,
        }
    )
    print('Patient:', patient.patient_id, patient.get_full_name())

    # Ensure an appointment type exists
    appt_type, _ = AppointmentType.objects.get_or_create(code='smoke_consult', defaults={
        'name': 'Smoke Consultation',
        'fee': Decimal('1500.00'),
    })

    # Create an appointment
    appt = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        appointment_type_new=appt_type,
        appointment_type='consultation',
        appointment_date=date.today(),
        appointment_time=datetime.now().time(),
        duration_minutes=30,
        fee=appt_type.fee,
        reason='Routine check',
        status='pending',
        created_by=doctor,
    )
    print('Created appointment id', appt.id)

    # Create a prescription
    pres = Prescription.objects.create(
        patient=patient,
        doctor=doctor,
        diagnosis='Test diagnosis',
        notes='Take as directed',
    )
    PrescriptionItem.objects.create(
        prescription=pres,
        medication_name='Amoxicillin',
        dosage='500mg',
        frequency='3 times daily',
        duration='7 days',
        quantity=21,
    )
    print('Created prescription id', pres.id)

    # Test patient search API using Django test client
    client = Client()
    resp = client.get('/patients/search-api/', {'q': patient.first_name})
    print('Search API status:', resp.status_code)
    try:
        print('Search results JSON:', resp.json())
    except Exception as e:
        print('Failed to parse JSON from search API:', e)

    # Reminder settings and appointment reminder
    settings_obj = ReminderSettings.get_settings()
    print('Reminder settings hours_before:', settings_obj.hours_before)

    reminder_time = datetime.now() + timedelta(hours=1)
    reminder = AppointmentReminder.objects.create(
        appointment=appt,
        reminder_time=reminder_time,
        status='pending',
        reminder_type='email',
    )
    print('Created reminder id', reminder.id, 'for appointment', appt.id)

    # Verify reminder exists for appointment
    reminders = appt.reminders.all()
    print('Appointment reminders count:', reminders.count())

    print('Smoke test completed successfully')


if __name__ == '__main__':
    run()

#!/usr/bin/env python
"""Quick test of appointment booking feature"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'galbose.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from appointments.models import Appointment, AppointmentType
from patients.models import Patient
from datetime import datetime, timedelta

def run_tests():
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    c = Client()
    c.force_login(user)

    p = Patient.objects.first()
    t = AppointmentType.objects.filter(is_active=True).first()
    dt = (datetime.now() + timedelta(days=3)).replace(microsecond=0)

    print("=" * 60)
    print("APPOINTMENT BOOKING TESTS")
    print("=" * 60)
    print()

    # Test 1: Create appointment
    print("TEST 1: Create Valid Appointment")
    data = {
        'patient': p.pk,
        'appointment_type_new': t.pk if t else '',
        'appointment_datetime': dt.strftime('%Y-%m-%dT%H:%M'),
        'duration_minutes': 30,
        'reason': 'Test_Booking_Valid',
        'status': 'pending'
    }
    resp = c.post('/appointments/create/', data, HTTP_HOST='127.0.0.1')
    appt_created = Appointment.objects.filter(reason='Test_Booking_Valid').exists()
    print(f"  Status Code: {resp.status_code}")
    print(f"  Redirect Location: {resp.get('Location')}")
    print(f"  Appointment Created in DB: {appt_created}")
    print(f"  ✓ PASS" if resp.status_code == 302 and appt_created else "  ✗ FAIL")
    print()

    # Test 2: List appointments
    print("TEST 2: List Appointments")
    resp = c.get('/appointments/', HTTP_HOST='127.0.0.1')
    print(f"  Status Code: {resp.status_code}")
    print(f"  Contains 'Book Appointment' button: {b'Book Appointment' in resp.content}")
    print(f"  ✓ PASS" if resp.status_code == 200 else "  ✗ FAIL")
    print()

    # Test 3: Get appointment detail
    print("TEST 3: View Appointment Detail")
    appt = Appointment.objects.filter(reason='Test_Booking_Valid').first()
    if appt:
        resp = c.get(f'/appointments/{appt.pk}/', HTTP_HOST='127.0.0.1')
        has_patient = p.get_full_name().encode() in resp.content
        has_reason = b'Test_Booking_Valid' in resp.content
        print(f"  Status Code: {resp.status_code}")
        print(f"  Contains Patient Name: {has_patient}")
        print(f"  Contains Reason: {has_reason}")
        print(f"  ✓ PASS" if resp.status_code == 200 and has_patient and has_reason else "  ✗ FAIL")
    else:
        print("  ✗ FAIL - Appointment not found")
    print()

    # Test 4: Past date validation
    print("TEST 4: Reject Past Date")
    data_past = data.copy()
    data_past['appointment_datetime'] = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M')
    data_past['reason'] = 'Test_Booking_Past'
    resp = c.post('/appointments/create/', data_past, HTTP_HOST='127.0.0.1')
    not_created = not Appointment.objects.filter(reason='Test_Booking_Past').exists()
    print(f"  Status Code: {resp.status_code}")
    print(f"  Did NOT redirect (302): {resp.status_code != 302}")
    print(f"  Appointment NOT created: {not_created}")
    print(f"  ✓ PASS" if resp.status_code == 200 and not_created else "  ✗ FAIL")
    print()

    # Test 5: Missing required field
    print("TEST 5: Reject Missing Required Field")
    data_missing = data.copy()
    del data_missing['reason']
    resp = c.post('/appointments/create/', data_missing, HTTP_HOST='127.0.0.1')
    has_error = b'error' in resp.content.lower() or b'required' in resp.content.lower()
    print(f"  Status Code: {resp.status_code}")
    print(f"  Did NOT redirect (302): {resp.status_code != 302}")
    print(f"  Response has error/required message: {has_error}")
    print(f"  ✓ PASS" if resp.status_code == 200 else "  ✗ FAIL")
    print()

    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()

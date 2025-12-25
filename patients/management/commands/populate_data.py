from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from accounts.models import User
from staff.models import Department, Ward, Bed, StaffSchedule
from patients.models import Patient, PatientVisit
from appointments.models import Appointment
from medical_records.models import Prescription, PrescriptionItem, LabTest, Diagnosis
from billing.models import Invoice, InvoiceItem, Payment
from pharmacy.models import Medication, StockAdjustment


class Command(BaseCommand):
    help = 'Populate database with sample hospital data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create departments
        self.create_departments()
        
        # Create staff
        self.create_staff()
        
        # Create wards and beds
        self.create_wards_and_beds()
        
        # Create medications
        self.create_medications()
        
        # Create patients
        self.create_patients()
        
        # Create appointments
        self.create_appointments()
        
        # Create medical records
        self.create_medical_records()
        
        # Create invoices and payments
        self.create_billing()
        
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now login and explore the system.'))

    def create_departments(self):
        self.stdout.write('Creating departments...')
        departments_data = [
            ('Emergency', 'Emergency and trauma care'),
            ('Cardiology', 'Heart and cardiovascular care'),
            ('Pediatrics', 'Children healthcare'),
            ('Obstetrics & Gynecology', 'Women and maternal health'),
            ('Surgery', 'Surgical procedures'),
            ('Internal Medicine', 'General internal medicine'),
            ('Radiology', 'Medical imaging'),
            ('Laboratory', 'Medical testing and diagnostics'),
            ('Pharmacy', 'Medication dispensing'),
        ]
        
        for name, desc in departments_data:
            Department.objects.get_or_create(name=name, defaults={'description': desc})
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(departments_data)} departments'))

    def create_staff(self):
        self.stdout.write('Creating staff members...')
        
        departments = list(Department.objects.all())
        
        # Doctors
        doctors_data = [
            ('John', 'Adamu', 'doctor', 'Cardiology'),
            ('Sarah', 'Bello', 'doctor', 'Pediatrics'),
            ('Michael', 'Chioma', 'doctor', 'Surgery'),
            ('Fatima', 'Danjuma', 'doctor', 'Obstetrics & Gynecology'),
            ('David', 'Eze', 'doctor', 'Internal Medicine'),
        ]
        
        for first, last, role, dept_name in doctors_data:
            dept = Department.objects.get(name=dept_name)
            User.objects.get_or_create(
                username=f'{first.lower()}.{last.lower()}',
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{first.lower()}.{last.lower()}@galbose.com',
                    'role': role,
                    'department': dept,
                    'phone': f'080{random.randint(10000000, 99999999)}',
                }
            )
        
        # Nurses
        nurses_data = [
            ('Grace', 'Ibrahim', 'nurse'),
            ('Mary', 'James', 'nurse'),
            ('Ruth', 'Kalu', 'nurse'),
        ]
        
        for first, last, role in nurses_data:
            User.objects.get_or_create(
                username=f'{first.lower()}.{last.lower()}',
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{first.lower()}.{last.lower()}@galbose.com',
                    'role': role,
                    'department': random.choice(departments),
                    'phone': f'080{random.randint(10000000, 99999999)}',
                }
            )
        
        # Other staff
        other_staff = [
            ('Ahmed', 'Mohammed', 'pharmacist', 'Pharmacy'),
            ('Joy', 'Okafor', 'receptionist', 'Emergency'),
            ('Peter', 'Usman', 'lab_technician', 'Laboratory'),
            ('Blessing', 'Yusuf', 'accountant', 'Emergency'),
        ]
        
        for first, last, role, dept_name in other_staff:
            dept = Department.objects.get(name=dept_name)
            User.objects.get_or_create(
                username=f'{first.lower()}.{last.lower()}',
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{first.lower()}.{last.lower()}@galbose.com',
                    'role': role,
                    'department': dept,
                    'phone': f'080{random.randint(10000000, 99999999)}',
                }
            )
        
        total_staff = len(doctors_data) + len(nurses_data) + len(other_staff)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {total_staff} staff members'))

    def create_wards_and_beds(self):
        self.stdout.write('Creating wards and beds...')
        
        wards_data = [
            ('General Ward A', 'Emergency', 10),
            ('General Ward B', 'Internal Medicine', 10),
            ('Pediatric Ward', 'Pediatrics', 8),
            ('Maternity Ward', 'Obstetrics & Gynecology', 6),
            ('ICU', 'Emergency', 5),
        ]
        
        total_beds = 0
        for ward_name, dept_name, capacity in wards_data:
            dept = Department.objects.get(name=dept_name)
            ward, created = Ward.objects.get_or_create(
                name=ward_name,
                department=dept,
                defaults={'capacity': capacity}
            )
            
            # Create beds
            for i in range(1, capacity + 1):
                Bed.objects.get_or_create(
                    ward=ward,
                    bed_number=f'{i:02d}',
                )
                total_beds += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(wards_data)} wards with {total_beds} beds'))

    def create_medications(self):
        self.stdout.write('Creating medications...')
        
        medications_data = [
            ('Paracetamol', 'Acetaminophen', 'tablet', '500mg', 500, 50, 50),
            ('Amoxicillin', 'Amoxicillin', 'capsule', '500mg', 300, 30, 150),
            ('Ibuprofen', 'Ibuprofen', 'tablet', '400mg', 400, 40, 75),
            ('Metformin', 'Metformin', 'tablet', '500mg', 200, 20, 100),
            ('Omeprazole', 'Omeprazole', 'capsule', '20mg', 250, 25, 120),
            ('Ciprofloxacin', 'Ciprofloxacin', 'tablet', '500mg', 150, 15, 200),
            ('Cough Syrup', 'Dextromethorphan', 'syrup', '100ml', 100, 10, 300),
            ('Insulin', 'Insulin', 'injection', '10ml', 80, 10, 500),
            ('Hydrocortisone Cream', 'Hydrocortisone', 'cream', '15g', 60, 10, 250),
            ('Eye Drops', 'Chloramphenicol', 'drops', '10ml', 90, 10, 180),
        ]
        
        for name, generic, category, dosage, stock, reorder, price in medications_data:
            Medication.objects.get_or_create(
                name=name,
                defaults={
                    'generic_name': generic,
                    'category': category,
                    'dosage_form': dosage,
                    'quantity_in_stock': stock,
                    'reorder_level': reorder,
                    'unit_price': Decimal(price),
                    'manufacturer': 'Generic Pharma Ltd.',
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(medications_data)} medications'))

    def create_patients(self):
        self.stdout.write('Creating patients...')
        
        first_names = ['Abubakar', 'Blessing', 'Chidi', 'Deborah', 'Emmanuel', 'Fatima', 
                      'Grace', 'Hassan', 'Ifeoma', 'James', 'Khadija', 'Ladi', 'Musa', 
                      'Ngozi', 'Ojo', 'Patricia', 'Rasheed', 'Sarah', 'Tunde', 'Uche']
        last_names = ['Adamu', 'Bello', 'Chioma', 'Danjuma', 'Eze', 'Garba', 'Hassan', 
                     'Ibrahim', 'James', 'Kalu', 'Lawan', 'Mohammed', 'Nwosu', 'Okafor', 
                     'Peter', 'Sani', 'Usman', 'Yusuf', 'Zainab', 'Abdullahi']
        
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        genders = ['M', 'F']
        
        receptionist = User.objects.filter(role='receptionist').first()
        
        for i in range(30):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            # Random age between 1 and 80
            age = random.randint(1, 80)
            dob = datetime.now().date() - timedelta(days=age*365)
            
            Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                gender=random.choice(genders),
                blood_group=random.choice(blood_groups),
                phone=f'080{random.randint(10000000, 99999999)}',
                email=f'{first_name.lower()}.{last_name.lower()}@email.com',
                address=f'{random.randint(1, 100)} {random.choice(["Ahmadu Bello", "Ribadu", "Atiku", "Lamido"])} Street',
                city='Gimeta',
                state='Adamawa',
                emergency_contact_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                emergency_contact_phone=f'080{random.randint(10000000, 99999999)}',
                emergency_contact_relationship=random.choice(['Spouse', 'Parent', 'Sibling', 'Child']),
                allergies=random.choice(['None', 'Penicillin', 'Peanuts', 'None', 'None']),
                chronic_conditions=random.choice(['None', 'Diabetes', 'Hypertension', 'None', 'Asthma', 'None']),
                registered_by=receptionist,
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 30 patients'))

    def create_appointments(self):
        self.stdout.write('Creating appointments...')
        
        patients = list(Patient.objects.all()[:20])
        doctors = list(User.objects.filter(role='doctor'))
        receptionist = User.objects.filter(role='receptionist').first()
        
        statuses = ['pending', 'confirmed', 'completed']
        appointment_types = ['consultation', 'follow_up', 'checkup']
        
        # Create appointments for the past week and next 2 weeks
        for i in range(40):
            days_offset = random.randint(-7, 14)
            appointment_date = (datetime.now() + timedelta(days=days_offset)).date()
            
            hour = random.randint(8, 16)
            appointment_time = datetime.strptime(f'{hour}:00', '%H:%M').time()
            
            status = 'completed' if days_offset < 0 else random.choice(statuses)
            
            Appointment.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                appointment_type=random.choice(appointment_types),
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                duration_minutes=30,
                reason=random.choice([
                    'General checkup',
                    'Follow-up consultation',
                    'Chest pain',
                    'Fever and cough',
                    'Routine examination',
                    'Blood pressure check',
                ]),
                status=status,
                created_by=receptionist,
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 40 appointments'))

    def create_medical_records(self):
        self.stdout.write('Creating medical records...')
        
        # Create patient visits
        completed_appointments = Appointment.objects.filter(status='completed')[:15]
        doctors = list(User.objects.filter(role='doctor'))
        
        for appointment in completed_appointments:
            visit = PatientVisit.objects.create(
                patient=appointment.patient,
                reason=appointment.reason,
                attending_doctor=appointment.doctor,
                vital_signs={
                    'temperature': f'{random.uniform(36.5, 37.5):.1f}°C',
                    'blood_pressure': f'{random.randint(110, 140)}/{random.randint(70, 90)}',
                    'pulse': f'{random.randint(60, 100)} bpm',
                    'weight': f'{random.randint(50, 90)} kg',
                },
                notes='Patient examined and treated.',
            )
            
            # Create prescription for some visits
            if random.random() > 0.3:
                prescription = Prescription.objects.create(
                    patient=appointment.patient,
                    doctor=appointment.doctor,
                    visit=visit,
                    diagnosis=random.choice([
                        'Upper respiratory tract infection',
                        'Hypertension',
                        'Diabetes mellitus',
                        'Gastritis',
                        'Migraine',
                    ]),
                    notes='Take medications as prescribed.',
                )
                
                # Add prescription items
                medications = list(Medication.objects.all()[:5])
                for _ in range(random.randint(1, 3)):
                    med = random.choice(medications)
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medication_name=med.name,
                        dosage=med.dosage_form,
                        frequency=random.choice(['Once daily', 'Twice daily', 'Three times daily']),
                        duration=random.choice(['3 days', '5 days', '7 days', '14 days']),
                        quantity=random.randint(10, 30),
                        instructions='Take after meals',
                    )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created medical records for {len(completed_appointments)} visits'))

    def create_billing(self):
        self.stdout.write('Creating invoices and payments...')
        
        patients = list(Patient.objects.all()[:15])
        accountant = User.objects.filter(role='accountant').first()
        
        for patient in patients:
            # Create invoice
            invoice = Invoice.objects.create(
                patient=patient,
                due_date=(datetime.now() + timedelta(days=30)).date(),
                status='issued',
                created_by=accountant,
            )
            
            # Add invoice items
            items_data = [
                ('Consultation Fee', random.randint(2000, 5000)),
                ('Lab Tests', random.randint(3000, 8000)),
                ('Medications', random.randint(1500, 6000)),
            ]
            
            for desc, price in random.sample(items_data, random.randint(1, 3)):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    item_type='consultation' if 'Consultation' in desc else 'medication' if 'Medication' in desc else 'lab_test',
                    description=desc,
                    quantity=1,
                    unit_price=Decimal(price),
                )
            
            # Calculate total
            invoice.calculate_total()
            
            # Create payment for some invoices
            if random.random() > 0.4:
                payment_amount = invoice.total if random.random() > 0.5 else invoice.total / 2
                Payment.objects.create(
                    invoice=invoice,
                    amount=payment_amount,
                    payment_method=random.choice(['cash', 'card', 'bank_transfer']),
                    received_by=accountant,
                )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(patients)} invoices with payments'))

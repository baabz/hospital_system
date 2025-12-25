# Galbose Hospital Management System

A comprehensive hospital management system built with Django for Galbose Hospital in Gimeta, Adamawa State, Nigeria.

## Features

- **Patient Management**: Register and manage patient records with unique IDs
- **Appointments**: Schedule and track patient appointments
- **Medical Records**: Prescriptions, lab tests, and diagnoses
- **Billing**: Invoice generation and payment tracking
- **Pharmacy**: Medication inventory with low-stock alerts
- **Staff Management**: Department and staff scheduling
- **Dashboard**: Real-time statistics and analytics
- **Role-Based Access**: Admin, Doctor, Nurse, Pharmacist, Receptionist, Accountant, Lab Technician

## Quick Start - Local Setup

### Prerequisites
- Python 3.11+
- Git (optional)

### Installation Steps

1. **Clone or navigate to the project directory**:
```bash
cd c:\Users\user\Desktop\galbose
```

2. **Activate the virtual environment** (Windows):
```powershell
.venv\Scripts\Activate.ps1
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Apply database migrations**:
```bash
python manage.py migrate
```

5. **Create a superuser account** (for admin access):
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

6. **Run the development server**:
```bash
python manage.py runserver
```

7. **Access the application**:
- Main Dashboard: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/

## Using the Application

### Creating Your First Prescription

**For Doctors:**
1. Navigate to "Patients" in the sidebar
2. Click on a patient's name to open their profile
3. Click the "📋 New Prescription" button
4. Fill in:
   - **Diagnosis**: Describe the patient's condition
   - **Doctor**: Your name (auto-filled if you're logged in as a doctor)
   - **Notes**: Any additional observations
5. Click "Create Prescription"
6. On the prescription detail page, click "➕ Add Medication" to add drugs
7. Fill in medication details (name, dosage, frequency, duration, quantity)
8. Save and the prescription is ready for the pharmacy to dispense

**For Pharmacists:**
1. Go to "Pharmacy" > "Medication List" to manage inventory
2. Go to "Pharmacy" > "Dispensing Records" to see pending prescriptions
3. Dispense medications from pending prescriptions

**For Receptionists:**
1. Visit "Patients" to register new patients or view existing ones
2. View a patient's prescription history in their profile
3. Click "📋 View All" to see complete prescription history

### Key Sections

#### Patients
- Register new patients with comprehensive medical history
- View allergies, chronic conditions, emergency contacts
- Track all appointments, visits, and prescriptions per patient

#### Appointments
- Book appointments for patients
- Track appointment status (pending, confirmed, completed)
- Assign doctors to appointments

#### Prescriptions
- Create prescriptions after patient visits
- Add multiple medications per prescription
- Track dispensing status
- View complete prescription history per patient

#### Medical Records
- Lab test ordering and result management
- Diagnosis tracking with follow-up dates
- Treatment plan documentation

#### Billing
- Generate invoices for patient services
- Track payment status
- View billing history

#### Pharmacy
- Manage medication inventory
- Track low-stock items
- Record medication dispensing

## Database

The application uses SQLite for local development (stored in `db.sqlite3`). The database schema includes:
- Users with role-based permissions
- Patients and patient visits
- Appointments and medical records
- Prescriptions with medication items
- Invoices and billing records
- Pharmacy inventory and dispensing records

## Technology Stack

- **Backend**: Django 5.2+
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS (Custom Design System), Alpine.js
- **PDF Generation**: ReportLab, WeasyPrint
- **Barcodes**: python-barcode, qrcode
- **Permissions**: Django-Guardian for object-level permissions

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, run:
```bash
python manage.py runserver 8001
```

### Database Issues
Reset the database and migrations:
```bash
# Delete db.sqlite3
rm db.sqlite3
# Reapply migrations
python manage.py migrate
```

### Missing Dependencies
Reinstall requirements:
```bash
pip install --upgrade -r requirements.txt
```

## Recent Fixes & Improvements

### Fixed Issues
- ✅ **Prescription Creation Fixed**: Doctors can now create prescriptions with proper validation
- ✅ **Doctor Auto-Assignment**: When a doctor creates a prescription, they're automatically assigned
- ✅ **Prescription History**: Added "View All Prescriptions" link on patient profile
- ✅ **Medication Management**: Pharmacists can dispense medications from prescriptions

### Features
- Complete prescription workflow from creation to dispensing
- Patient prescription history tracking
- Medication inventory management
- Lab test ordering and tracking
- Comprehensive patient profiles

## Support & Development

For issues or feature requests, contact the development team.

---

**Last Updated**: December 22, 2025

## Project Structure

```
galbose/
├── accounts/          # User authentication and roles
├── patients/          # Patient management
├── appointments/      # Appointment scheduling
├── medical_records/   # Prescriptions, lab tests, diagnoses
├── billing/           # Invoicing and payments
├── pharmacy/          # Medication inventory
├── staff/             # Staff and department management
├── dashboard/         # Main dashboard
├── reports/           # Report generation
├── static/            # CSS, JS, images
└── templates/         # HTML templates
```

## License

© 2025 Galbose Hospital. All rights reserved.

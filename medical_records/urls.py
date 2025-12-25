from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    # Prescriptions
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/create/', views.prescription_create, name='prescription_create'),
    path('prescriptions/create/<str:patient_id>/', views.prescription_create, name='prescription_create_for_patient'),
    path('prescriptions/create-from-appointment/<int:appointment_id>/', views.prescription_create, name='prescription_create_from_appointment'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:prescription_id>/add-item/', views.prescription_item_create, name='prescription_item_create'),
    
    # Lab Tests
    path('lab-tests/', views.lab_test_list, name='lab_test_list'),
    path('lab-tests/create/', views.lab_test_create, name='lab_test_create'),
    path('lab-tests/create/<str:patient_id>/', views.lab_test_create, name='lab_test_create_for_patient'),
    path('lab-tests/<int:pk>/', views.lab_test_detail, name='lab_test_detail'),
    path('lab-tests/<int:pk>/update/', views.lab_test_update, name='lab_test_update'),
    
    # Diagnoses
    path('diagnoses/', views.diagnosis_list, name='diagnosis_list'),
    path('diagnoses/create/', views.diagnosis_create, name='diagnosis_create'),
    path('diagnoses/create/<str:patient_id>/', views.diagnosis_create, name='diagnosis_create_for_patient'),
    
    # Clinical Documentation (NEW)
    path('visits/<int:visit_id>/vital-signs/', views.vital_signs_update, name='vital_signs_update'),
    path('visits/<int:visit_id>/clinical-notes/', views.clinical_notes_update, name='clinical_notes_update'),
    
    # Prescription Wizard (NEW)
    path('prescription-wizard/<str:patient_id>/', views.prescription_wizard, name='prescription_wizard'),
    path('prescription-wizard/<str:patient_id>/step/<int:step>/', views.prescription_wizard, name='prescription_wizard_step'),
]

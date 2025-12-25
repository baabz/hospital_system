from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    
    # Expenses (must come before invoice_detail to avoid conflict)
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('financial-report/', views.financial_report, name='financial_report'),
    
    # Invoice detail and related (must come after specific paths)
    path('<str:invoice_number>/', views.invoice_detail, name='invoice_detail'),
    path('<str:invoice_number>/add-item/', views.invoice_add_item, name='invoice_add_item'),
    path('<str:invoice_number>/record-payment/', views.invoice_record_payment, name='invoice_record_payment'),
]

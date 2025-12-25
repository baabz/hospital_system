from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Dashboard
    path('', views.accounting_dashboard, name='dashboard'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/record/', views.payment_record, name='payment_record'),
    
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/record/', views.expense_record, name='expense_record'),
    path('expenses/<int:pk>/approve/', views.expense_approve, name='expense_approve'),
    
    # Reports
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reconciliation/', views.cash_reconciliation, name='reconciliation'),
]

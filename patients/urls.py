from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_create, name='patient_create'),
    path('search-api/', views.patient_search_api, name='patient_search_api'),
    path('<str:patient_id>/', views.patient_detail, name='patient_detail'),
    path('<str:patient_id>/edit/', views.patient_update, name='patient_update'),
    path('<str:patient_id>/delete/', views.patient_delete, name='patient_delete'),
]

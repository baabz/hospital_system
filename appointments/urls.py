from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('calendar/', views.appointment_calendar, name='appointment_calendar'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('<int:pk>/start/', views.appointment_start_consultation, name='appointment_start_consultation'),
    path('<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
]

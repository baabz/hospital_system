from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.medication_list, name='medication_list'),
    path('dispensing/', views.dispensing_list, name='dispensing_list'),
]

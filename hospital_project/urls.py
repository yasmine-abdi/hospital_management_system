"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from hospital.views import login_view, dashboard_view
from django.contrib.auth.views import LogoutView # Import-garee LogoutView
from hospital.views import add_patient_view, patient_list_view
from hospital import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/'), name='home'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('add-patient/', add_patient_view, name='add_patient'),
    path('patient-list/', patient_list_view, name='patient_list'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/create/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/update/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/update/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),

    # Pharmacy URLs
    path('pharmacy/medicines/', views.medicine_list, name='medicine_list'),
    path('pharmacy/medicines/create/', views.medicine_create, name='medicine_create'),
    path('pharmacy/medicines/<int:pk>/update/', views.medicine_update, name='medicine_update'),
    path('pharmacy/medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    
    path('pharmacy/sales/', views.pharmacy_sale_list, name='pharmacy_sale_list'),
    path('pharmacy/sales/create/', views.pharmacy_sale_create, name='pharmacy_sale_create'),
    path('pharmacy/sales/<int:pk>/', views.pharmacy_sale_detail, name='pharmacy_sale_detail'),

    # Inpatient (IPD) URLs
    path('ipd/admissions/', views.admission_list, name='admission_list'),
    path('ipd/admissions/create/', views.admission_create, name='admission_create'),
    path('ipd/admissions/<int:pk>/update/', views.admission_update, name='admission_update'),
    path('ipd/admissions/<int:pk>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('ipd/beds/', views.bed_list, name='bed_list'),
    path('ipd/beds/create/', views.bed_create, name='bed_create'),
    path('ipd/wards/create/', views.ward_create, name='ward_create'),
]

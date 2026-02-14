"""
URLs برای بخش پزشکان - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    # لیست پزشکان (عمومی)
    path('', views.doctor_list, name='list'),
    path('<int:pk>/', views.doctor_detail, name='detail'),
]

# URL های پنل پزشک (در config/urls.py استفاده می‌شود)
doctor_panel_patterns = [
    # داشبورد
    path('', views.doctor_dashboard, name='doctor_dashboard'),
    
    # نوبت‌ها
    path('today/', views.doctor_today_appointments, name='doctor_today_appointments'),
    path('appointments/add/', views.doctor_add_appointment, name='doctor_add_appointment'),
    
    # تقویم و صف
    path('schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('schedule/delete/', views.doctor_delete_schedule, name='doctor_delete_schedule'),
    path('live-queue/', views.doctor_live_queue, name='doctor_live_queue'),
    
    # مدیریت مراکز (مطب، کلینیک، بیمارستان)
    path('clinics/', views.doctor_clinics, name='doctor_clinics'),
    path('clinics/add/', views.doctor_add_clinic, name='doctor_add_clinic'),
    path('clinics/link/', views.doctor_link_clinic, name='doctor_link_clinic'),
    path('clinics/<int:clinic_id>/edit/', views.doctor_edit_clinic, name='doctor_edit_clinic'),
    path('clinics/<int:clinic_id>/delete/', views.doctor_delete_clinic, name='doctor_delete_clinic'),
    path('clinics/<int:clinic_id>/set-primary/', views.doctor_set_primary_clinic, name='doctor_set_primary_clinic'),
    
    # بیماران
    path('patients/', views.doctor_patients, name='doctor_patients'),
    path('patients/<int:patient_id>/', views.doctor_patient_record, name='doctor_patient_record'),
    
    # پرونده‌ها
    path('records/', views.doctor_records, name='doctor_records'),
    path('records/add/<int:appointment_id>/', views.doctor_add_record, name='doctor_add_record'),
    path('records/new/', views.doctor_new_record, name='doctor_new_record'),
    
    # گزارش‌ها
    path('reports/', views.doctor_reports, name='doctor_reports'),
    
    # مرخصی‌ها
    path('holidays/', views.doctor_holidays, name='doctor_holidays'),
    path('holidays/add/', views.doctor_add_holiday, name='doctor_add_holiday'),
    
    # تعرفه‌ها
    path('tariffs/', views.doctor_tariffs, name='doctor_tariffs'),
    path('tariffs/add/', views.doctor_add_tariff, name='doctor_add_tariff'),
    path('tariffs/<int:tariff_id>/edit/', views.doctor_edit_tariff, name='doctor_edit_tariff'),
    path('tariffs/<int:tariff_id>/delete/', views.doctor_delete_tariff, name='doctor_delete_tariff'),
    path('tariffs/bulk/', views.doctor_bulk_tariffs, name='doctor_bulk_tariffs'),
    
    # منشی‌ها
    path('secretaries/', views.doctor_secretaries, name='doctor_secretaries'),
    path('secretaries/add/', views.doctor_add_secretary, name='doctor_add_secretary'),

    # تنظیمات
    path('settings/', views.doctor_settings, name='doctor_settings'),
]

# API ها
api_patterns = [
    # جستجوی بیمار
    path('patients/search/', views.api_search_patient, name='api_search_patient'),
    
    path('appointments/<int:appointment_id>/confirm/', views.api_confirm_appointment, name='api_confirm_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.api_cancel_appointment, name='api_cancel_appointment'),
    path('appointments/<int:appointment_id>/arrived/', views.api_mark_arrived, name='api_mark_arrived'),
    path('appointments/<int:appointment_id>/start-visit/', views.api_start_visit, name='api_start_visit'),
    path('appointments/<int:appointment_id>/end-visit/', views.api_end_visit, name='api_end_visit'),
    
    # API تعرفه‌ها
    path('doctors/<int:doctor_id>/tariff/calculate/', views.api_calculate_tariff, name='api_calculate_tariff'),
    path('doctors/<int:doctor_id>/services/', views.api_doctor_services, name='api_doctor_services'),
    path('doctors/<int:doctor_id>/services/<int:service_id>/insurances/', views.api_doctor_insurances, name='api_doctor_insurances'),
    
    # API اصطلاحات پزشکی (autocomplete)
    path('medical-terms/', views.api_medical_terms, name='api_medical_terms'),
    path('medical-terms/add/', views.api_add_medical_term, name='api_add_medical_term'),
]

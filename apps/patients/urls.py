"""
URLs برای بخش بیماران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.urls import path
from . import views

urlpatterns = [
    # داشبورد
    path('', views.patient_dashboard, name='patient_dashboard'),

    # رزرو نوبت
    path('book/', views.book_appointment, name='patient_book_appointment'),
    path('book/<int:doctor_id>/', views.book_appointment_doctor, name='patient_book_doctor'),

    # API رزرو (AJAX)
    path('book/<int:doctor_id>/dates/', views.api_doctor_dates, name='api_doctor_dates'),
    path('book/<int:doctor_id>/times/', views.api_doctor_times, name='api_doctor_times'),

    # نوبت‌های من
    path('appointments/', views.my_appointments, name='patient_appointments'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='patient_cancel_appointment'),

    # صف زنده
    path('queue/', views.live_queue, name='patient_queue'),

    # پرونده پزشکی
    path('records/', views.medical_records, name='patient_records'),
    path('records/<int:pk>/', views.record_detail, name='patient_record_detail'),

    # نسخه‌ها
    path('prescriptions/', views.prescriptions, name='patient_prescriptions'),

    # فایل‌های پزشکی
    path('files/', views.medical_files, name='patient_files'),
    path('files/upload/', views.upload_file, name='patient_upload_file'),

    # پرداخت‌ها
    path('payments/', views.payments, name='patient_payments'),
]

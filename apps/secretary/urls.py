"""
URLs برای بخش منشی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.urls import path
from . import views

urlpatterns = [
    # داشبورد
    path('', views.secretary_dashboard, name='secretary_dashboard'),

    # نوبت‌های امروز
    path('today/', views.secretary_today, name='secretary_today'),

    # صف زنده
    path('queue/', views.secretary_live_queue, name='secretary_live_queue'),

    # لیست همه نوبت‌ها
    path('appointments/', views.secretary_appointments, name='secretary_appointments'),

    # ثبت نوبت حضوری
    path('appointments/add/', views.secretary_add_appointment, name='secretary_add_appointment'),

    # بیماران
    path('patients/', views.secretary_patients, name='secretary_patients'),

    # پرداخت‌ها
    path('payments/', views.secretary_payments, name='secretary_payments'),

    # API تغییر وضعیت نوبت
    path('api/appointment/<int:appointment_id>/action/', views.api_appointment_action, name='secretary_appointment_action'),

    # API جستجوی بیمار
    path('api/patients/search/', views.api_secretary_search_patient, name='secretary_api_search_patient'),
]

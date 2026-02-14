"""
URLs پنل مدیریت سیستم (SuperAdmin) - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.urls import path
from . import admin_views as views

urlpatterns = [
    # داشبورد
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('health/', views.admin_system_health, name='admin_system_health'),

    # پزشکان
    path('doctors/', views.admin_doctors, name='admin_doctors'),
    path('doctors/add/', views.admin_doctor_add, name='admin_doctor_add'),
    path('doctors/<int:doctor_id>/edit/', views.admin_doctor_edit, name='admin_doctor_edit'),
    path('doctors/<int:doctor_id>/detail/', views.admin_doctor_detail, name='admin_doctor_detail'),
    path('doctors/<int:doctor_id>/toggle/', views.admin_doctor_toggle, name='admin_doctor_toggle'),

    # مراکز
    path('clinics/', views.admin_clinics, name='admin_clinics'),
    path('clinics/add/', views.admin_clinic_add, name='admin_clinic_add'),
    path('clinics/<int:clinic_id>/edit/', views.admin_clinic_edit, name='admin_clinic_edit'),

    # کاربران
    path('users/', views.admin_users, name='admin_users'),
    path('users/add/', views.admin_user_add, name='admin_user_add'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('users/<int:user_id>/toggle/', views.admin_user_toggle, name='admin_user_toggle'),

    # درگاه پرداخت
    path('gateways/', views.admin_gateways, name='admin_gateways'),
    path('gateways/save/', views.admin_gateways_save, name='admin_gateway_save'),

    # پلن‌ها
    path('plans/', views.admin_plans, name='admin_plans'),
    path('plans/add/', views.admin_plan_add, name='admin_plan_add'),
    path('plans/<int:plan_id>/edit/', views.admin_plan_edit, name='admin_plan_edit'),

    # تراکنش‌ها
    path('transactions/', views.admin_transactions, name='admin_transactions'),

    # گزارش‌ها
    path('reports/', views.admin_reports, name='admin_reports'),

    # لاگ
    path('logs/', views.admin_logs, name='admin_logs'),

    # تنظیمات
    path('settings/', views.admin_settings, name='admin_settings'),
    path('settings/save/', views.admin_settings_save, name='admin_settings_save'),

    # پیامک
    path('sms/', views.admin_sms, name='admin_sms'),
    path('sms/save/', views.admin_sms_save, name='admin_sms_save'),
    path('sms/templates/save/', views.admin_sms_templates_save, name='admin_sms_templates_save'),
]

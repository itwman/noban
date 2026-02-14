"""
تنظیمات اپلیکیشن نوبت‌دهی - نوبان
"""

from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'مدیریت نوبت‌ها'

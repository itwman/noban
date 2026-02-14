"""
تنظیمات اپلیکیشن پرداخت - نوبان
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    verbose_name = 'مدیریت پرداخت'

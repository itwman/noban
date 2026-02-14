"""
URLs برای بخش نوبت‌دهی - نوبان
"""

from django.urls import path
from . import views

urlpatterns = [
    # نوبت‌ها (برای همه کاربران)
    path('', views.appointment_list, name='appointment_list'),
]

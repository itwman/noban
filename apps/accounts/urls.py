"""
URLs برای اپلیکیشن accounts - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.urls import path
from . import views

urlpatterns = [
    # صفحه اصلی
    path('', views.home, name='home'),
    
    # احراز هویت
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # بازیابی رمز عبور
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # پنل کاربری
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
]

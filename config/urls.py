"""
URL Configuration for NoBan project

نرم‌افزار نوبان - سیستم رزرو و مدیریت نوبت پزشکان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import doctor panel patterns
from apps.doctors.urls import doctor_panel_patterns, api_patterns as doctor_api_patterns

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Installer
    path('install/', include('installer.urls')),
    
    # پنل مدیریت سیستم (SuperAdmin)
    path('management/', include('apps.core.admin_urls')),
    
    # صفحات اصلی (accounts)
    path('', include('apps.accounts.urls')),
    
    # بخش بیماران
    path('patient/', include('apps.patients.urls')),
    
    # بخش منشی
    path('secretary/', include('apps.secretary.urls')),
    
    # بخش پزشکان (عمومی)
    path('doctors/', include('apps.doctors.urls')),
    
    # پنل پزشک
    path('doctor/', include(doctor_panel_patterns)),
    
    # بخش نوبت‌دهی
    path('appointments/', include('apps.appointments.urls')),
    
    # API Endpoints
    path('api/', include(doctor_api_patterns)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Admin Site Configuration
admin.site.site_header = "نوبان - پنل مدیریت"
admin.site.site_title = "مدیریت نوبان"
admin.site.index_title = "خوش آمدید به پنل مدیریت نوبان"

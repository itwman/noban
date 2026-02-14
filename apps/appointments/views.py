"""
Views برای بخش نوبت‌دهی - نوبان
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment


@login_required
def appointment_list(request):
    """لیست نوبت‌ها"""
    # هدایت به صفحه مناسب بر اساس نقش
    if request.user.role == 'patient':
        return redirect('patient_appointments')
    elif request.user.role == 'doctor':
        return redirect('dashboard')
    else:
        return redirect('dashboard')

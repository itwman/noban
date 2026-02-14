"""
Views برای بخش منشی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان

پنل کامل منشی شامل:
- داشبورد با آمار زنده
- نوبت‌های امروز (تأیید، پذیرش، شروع/پایان ویزیت، لغو)
- صف زنده با کنترل کامل
- ثبت نوبت حضوری
- جستجوی بیمار
- لیست همه نوبت‌ها
- پرداخت‌ها
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import timedelta, datetime

from apps.appointments.models import Appointment
from apps.doctors.models import Doctor, DoctorClinic, WorkSchedule
from apps.clinics.models import Clinic
from apps.accounts.models import User


# ============================================================
#  توابع کمکی
# ============================================================

def secretary_required(view_func):
    """دکوراتور: فقط منشی یا مدیرکل"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ['secretary', 'superadmin']:
            messages.error(request, 'شما دسترسی به این بخش ندارید.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_secretary_doctor(user):
    """دریافت پزشک مرتبط با منشی"""
    # TODO: وقتی مدل ارتباط منشی-پزشک اضافه شد اینجا تغییر کند
    return Doctor.objects.filter(is_active=True).select_related('user').first()


def get_secretary_clinic(user, doctor):
    """دریافت مرکز فعال منشی"""
    if doctor:
        dc = DoctorClinic.objects.filter(doctor=doctor).select_related('clinic').first()
        if dc:
            return dc.clinic
    return None


# ============================================================
#  داشبورد
# ============================================================

@secretary_required
def secretary_dashboard(request):
    """داشبورد اصلی منشی"""
    today = timezone.now().date()
    doctor = get_secretary_doctor(request.user)
    clinic = get_secretary_clinic(request.user, doctor)

    if not doctor:
        return render(request, 'secretary/dashboard.html', {'no_doctor': True})

    # نوبت‌های امروز
    today_qs = Appointment.objects.filter(
        doctor=doctor, date=today,
    ).select_related('patient', 'clinic')
    if clinic:
        today_qs = today_qs.filter(clinic=clinic)

    today_appointments = today_qs.order_by('time')

    # آمار
    total_today = today_appointments.count()
    pending_count = today_appointments.filter(status='pending').count()
    confirmed_count = today_appointments.filter(status='confirmed').count()
    arrived_count = today_appointments.filter(status='arrived').count()
    in_progress_count = today_appointments.filter(status='in_progress').count()
    visited_count = today_appointments.filter(status='visited').count()
    cancelled_count = today_appointments.filter(status='cancelled').count()
    waiting_count = pending_count + confirmed_count + arrived_count

    # بیمار در حال ویزیت
    current_patient = today_appointments.filter(status='in_progress').first()
    # نفر بعدی
    next_patient = today_appointments.filter(
        status__in=['arrived', 'confirmed']
    ).order_by('queue_number', 'time').first()

    # آمار هفتگی
    week_start = today - timedelta(days=6)
    week_qs = Appointment.objects.filter(doctor=doctor, date__gte=week_start, date__lte=today)
    if clinic:
        week_qs = week_qs.filter(clinic=clinic)

    context = {
        'doctor': doctor,
        'clinic': clinic,
        'today_appointments': today_appointments[:15],
        'total_today': total_today,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'arrived_count': arrived_count,
        'in_progress_count': in_progress_count,
        'visited_count': visited_count,
        'cancelled_count': cancelled_count,
        'waiting_count': waiting_count,
        'current_patient': current_patient,
        'next_patient': next_patient,
        'week_total': week_qs.count(),
        'week_visited': week_qs.filter(status='visited').count(),
    }
    return render(request, 'secretary/dashboard.html', context)


# ============================================================
#  نوبت‌های امروز
# ============================================================

@secretary_required
def secretary_today(request):
    """نوبت‌های امروز"""
    today = timezone.now().date()
    doctor = get_secretary_doctor(request.user)
    clinic = get_secretary_clinic(request.user, doctor)

    if not doctor:
        return redirect('secretary_dashboard')

    qs = Appointment.objects.filter(doctor=doctor, date=today).select_related('patient', 'clinic')
    if clinic:
        qs = qs.filter(clinic=clinic)

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    context = {
        'doctor': doctor,
        'clinic': clinic,
        'appointments': qs.order_by('time'),
        'status_filter': status_filter,
    }
    return render(request, 'secretary/today.html', context)


# ============================================================
#  صف زنده
# ============================================================

@secretary_required
def secretary_live_queue(request):
    """صف زنده - کنترل کامل"""
    today = timezone.now().date()
    doctor = get_secretary_doctor(request.user)
    clinic = get_secretary_clinic(request.user, doctor)

    if not doctor:
        return redirect('secretary_dashboard')

    qs = Appointment.objects.filter(doctor=doctor, date=today).select_related('patient', 'clinic')
    if clinic:
        qs = qs.filter(clinic=clinic)

    context = {
        'doctor': doctor,
        'clinic': clinic,
        'waiting': qs.filter(status__in=['confirmed', 'arrived']).order_by('queue_number', 'time'),
        'in_progress': qs.filter(status='in_progress').first(),
        'visited': qs.filter(status='visited').order_by('-visited_at'),
        'pending': qs.filter(status='pending').order_by('time'),
        'waiting_count': qs.filter(status__in=['confirmed', 'arrived']).count(),
        'visited_count': qs.filter(status='visited').count(),
        'total_today': qs.exclude(status='cancelled').count(),
    }
    return render(request, 'secretary/live_queue.html', context)


# ============================================================
#  لیست همه نوبت‌ها
# ============================================================

@secretary_required
def secretary_appointments(request):
    """لیست نوبت‌ها با فیلتر"""
    doctor = get_secretary_doctor(request.user)
    clinic = get_secretary_clinic(request.user, doctor)
    today = timezone.now().date()

    if not doctor:
        return redirect('secretary_dashboard')

    qs = Appointment.objects.filter(doctor=doctor).select_related('patient', 'clinic')
    if clinic:
        qs = qs.filter(clinic=clinic)

    period = request.GET.get('period', 'upcoming')
    if period == 'today':
        qs = qs.filter(date=today)
    elif period == 'upcoming':
        qs = qs.filter(date__gte=today)
    elif period == 'past':
        qs = qs.filter(date__lt=today)
    elif period == 'week':
        qs = qs.filter(date__gte=today, date__lte=today + timedelta(days=7))

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    search = request.GET.get('q', '')
    if search:
        qs = qs.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(patient__phone__icontains=search)
        )

    context = {
        'doctor': doctor,
        'appointments': qs.order_by('-date', 'time')[:100],
        'period': period,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'secretary/appointments.html', context)


# ============================================================
#  ثبت نوبت حضوری
# ============================================================

@secretary_required
def secretary_add_appointment(request):
    """ثبت نوبت حضوری توسط منشی"""
    doctor = get_secretary_doctor(request.user)
    clinic = get_secretary_clinic(request.user, doctor)

    if not doctor:
        return redirect('secretary_dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        date_str = request.POST.get('date', '').strip()
        time_str = request.POST.get('time', '').strip()
        notes = request.POST.get('notes', '').strip()

        if not phone or not date_str or not time_str:
            messages.error(request, 'شماره موبایل، تاریخ و ساعت الزامی است.')
            return redirect('secretary_add_appointment')

        # پیدا کردن یا ایجاد بیمار
        patient, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'first_name': first_name or 'بیمار',
                'last_name': last_name or 'جدید',
                'role': 'patient',
            }
        )
        if created:
            patient.set_unusable_password()
            patient.save()

        try:
            appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            appt_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, 'فرمت تاریخ یا ساعت نامعتبر است.')
            return redirect('secretary_add_appointment')

        # بررسی تکراری
        if Appointment.objects.filter(
            doctor=doctor, date=appt_date, time=appt_time,
        ).exclude(status='cancelled').exists():
            messages.error(request, 'این ساعت قبلاً رزرو شده است.')
            return redirect('secretary_add_appointment')

        # شماره صف
        last_queue = Appointment.objects.filter(
            doctor=doctor, date=appt_date,
        ).exclude(status='cancelled').count()

        target_clinic = clinic or Clinic.objects.first()
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            clinic=target_clinic,
            date=appt_date,
            time=appt_time,
            status='confirmed',
            queue_number=last_queue + 1,
            booking_source='secretary',
            secretary_notes=notes,
        )

        messages.success(request, f'نوبت برای {patient.get_full_name()} ثبت شد. شماره صف: {appointment.queue_number}')
        return redirect('secretary_today')

    context = {
        'doctor': doctor,
        'clinic': clinic,
    }
    return render(request, 'secretary/add_appointment.html', context)


# ============================================================
#  بیماران
# ============================================================

@secretary_required
def secretary_patients(request):
    """لیست و جستجوی بیماران"""
    doctor = get_secretary_doctor(request.user)
    search = request.GET.get('q', '')
    patients = User.objects.none()

    if search:
        patients = User.objects.filter(role='patient').filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(national_code__icontains=search)
        )[:30]
    elif doctor:
        patient_ids = Appointment.objects.filter(
            doctor=doctor
        ).values_list('patient_id', flat=True).distinct()
        patients = User.objects.filter(id__in=patient_ids, role='patient').order_by('-date_joined')[:30]

    context = {
        'patients': patients,
        'search': search,
        'doctor': doctor,
    }
    return render(request, 'secretary/patients.html', context)


# ============================================================
#  پرداخت‌ها
# ============================================================

@secretary_required
def secretary_payments(request):
    """لیست پرداخت‌ها"""
    doctor = get_secretary_doctor(request.user)
    today = timezone.now().date()

    if not doctor:
        return redirect('secretary_dashboard')

    qs = Appointment.objects.filter(doctor=doctor).exclude(
        payment_status='unpaid'
    ).select_related('patient', 'clinic').order_by('-date', '-time')

    period = request.GET.get('period', 'today')
    if period == 'today':
        qs = qs.filter(date=today)
    elif period == 'week':
        qs = qs.filter(date__gte=today - timedelta(days=7))
    elif period == 'month':
        qs = qs.filter(date__gte=today - timedelta(days=30))

    total_amount = qs.aggregate(total=Sum('tariff_fee'))['total'] or 0

    context = {
        'doctor': doctor,
        'payments': qs[:50],
        'period': period,
        'total_amount': total_amount,
    }
    return render(request, 'secretary/payments.html', context)


# ============================================================
#  API تغییر وضعیت نوبت
# ============================================================

@secretary_required
def api_appointment_action(request, appointment_id):
    """API تغییر وضعیت نوبت (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'روش نامعتبر'}, status=405)

    action = request.POST.get('action', '')
    appointment = get_object_or_404(Appointment, id=appointment_id)

    valid_actions = {
        'confirm': {'from': ['pending'], 'to': 'confirmed', 'msg': 'نوبت تأیید شد.'},
        'arrive': {'from': ['confirmed', 'pending'], 'to': 'arrived', 'msg': 'حضور بیمار ثبت شد.'},
        'start_visit': {'from': ['arrived', 'confirmed'], 'to': 'in_progress', 'msg': 'ویزیت شروع شد.'},
        'end_visit': {'from': ['in_progress'], 'to': 'visited', 'msg': 'ویزیت پایان یافت.'},
        'cancel': {'from': ['pending', 'confirmed'], 'to': 'cancelled', 'msg': 'نوبت لغو شد.'},
        'no_show': {'from': ['pending', 'confirmed', 'arrived'], 'to': 'no_show', 'msg': 'عدم حضور ثبت شد.'},
    }

    if action not in valid_actions:
        return JsonResponse({'success': False, 'message': 'عملیات نامعتبر'})

    rule = valid_actions[action]
    if appointment.status not in rule['from']:
        return JsonResponse({
            'success': False,
            'message': f'وضعیت فعلی ({appointment.get_status_display()}) اجازه این عملیات را نمی‌دهد.'
        })

    appointment.status = rule['to']
    if action == 'arrive':
        appointment.arrived_at = timezone.now()
    elif action in ['start_visit', 'end_visit']:
        appointment.visited_at = timezone.now()
    elif action == 'cancel':
        appointment.cancelled_at = timezone.now()
        appointment.cancel_reason = request.POST.get('reason', 'لغو توسط منشی')

    appointment.save()

    return JsonResponse({
        'success': True,
        'message': rule['msg'],
        'new_status': appointment.status,
        'new_status_display': appointment.get_status_display(),
        'new_badge_class': appointment.get_status_badge_class(),
    })


@secretary_required
def api_secretary_search_patient(request):
    """API جستجوی بیمار (AJAX)"""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    patients = User.objects.filter(role='patient').filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q)
    )[:10]

    return JsonResponse({'results': [
        {'id': p.id, 'name': p.get_full_name(), 'phone': p.phone}
        for p in patients
    ]})

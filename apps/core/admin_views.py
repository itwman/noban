"""
Views پنل مدیریت سیستم (SuperAdmin) - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from functools import wraps
from datetime import timedelta


# =============================================================================
# دکوراتور بررسی دسترسی ادمین
# =============================================================================

def superadmin_required(view_func):
    """دکوراتور بررسی دسترسی مدیر سیستم"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.role == 'superadmin' or request.user.is_superuser):
            messages.error(request, 'شما دسترسی به این بخش ندارید')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# داشبورد
# =============================================================================

@superadmin_required
def admin_dashboard(request):
    """داشبورد مدیر سیستم"""
    from apps.accounts.models import User
    from apps.doctors.models import Doctor
    from apps.clinics.models import Clinic
    from apps.appointments.models import Appointment

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # آمار کلی
    total_doctors = Doctor.objects.filter(is_active=True).count()
    total_clinics = Clinic.objects.filter(is_active=True).count()
    total_patients = User.objects.filter(role='patient', is_active=True).count()
    today_appointments = Appointment.objects.filter(date=today).exclude(status='cancelled').count()

    # درآمد ماهانه
    monthly_revenue = Appointment.objects.filter(
        date__gte=month_start,
        payment_status='paid'
    ).aggregate(total=Sum('payment_amount'))['total'] or 0

    # نوبت‌های اخیر
    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor', 'doctor__user', 'clinic'
    ).order_by('-created_at')[:10]

    context = {
        'active_page': 'dashboard',
        'total_doctors': total_doctors,
        'total_clinics': total_clinics,
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'monthly_revenue': monthly_revenue,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# =============================================================================
# سلامت سیستم
# =============================================================================

@superadmin_required
def admin_system_health(request):
    """صفحه سلامت سیستم"""
    import shutil

    # بررسی فضای دیسک
    try:
        disk = shutil.disk_usage('/')
        disk_percent = int((disk.used / disk.total) * 100)
    except Exception:
        disk_percent = 0

    # بررسی اتصال دیتابیس
    from django.db import connection
    try:
        connection.ensure_connection()
        db_status = 'operational'
    except Exception:
        db_status = 'down'

    context = {
        'active_page': 'health',
        'db_status': db_status,
        'disk_percent': disk_percent,
        'web_status': 'operational',
    }
    return render(request, 'admin_panel/system_health.html', context)


# =============================================================================
# مدیریت پزشکان
# =============================================================================

@superadmin_required
def admin_doctors(request):
    """لیست پزشکان"""
    from apps.doctors.models import Doctor
    from apps.appointments.models import Appointment

    today = timezone.now().date()
    doctors = Doctor.objects.select_related('user').all().order_by('-created_at')

    # افزودن تعداد نوبت امروز به هر پزشک
    for doc in doctors:
        doc.today_count = Appointment.objects.filter(
            doctor=doc, date=today
        ).exclude(status='cancelled').count()

    context = {
        'active_page': 'doctors',
        'doctors': doctors,
    }
    return render(request, 'admin_panel/doctors.html', context)


@superadmin_required
def admin_doctor_add(request):
    """افزودن پزشک"""
    from apps.accounts.models import User
    from apps.doctors.models import Doctor
    from apps.clinics.models import Clinic

    if request.method == 'POST':
        try:
            # ایجاد کاربر
            user = User.objects.create_user(
                phone=request.POST.get('phone'),
                password=request.POST.get('phone'),  # رمز پیش‌فرض = شماره موبایل
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                role='doctor',
            )
            # ایجاد پروفایل پزشک
            doctor = Doctor.objects.create(
                user=user,
                medical_code=request.POST.get('medical_code', ''),
                specialization=request.POST.get('specialization', ''),
                visit_duration=int(request.POST.get('visit_duration', 15)),
                gap_between_visits=int(request.POST.get('gap_between_visits', 5)),
                max_daily_appointments=int(request.POST.get('max_daily_appointments', 30)),
                bio=request.POST.get('bio', ''),
            )
            # اتصال به مرکز
            clinic_id = request.POST.get('clinic')
            if clinic_id:
                from apps.doctors.models import DoctorClinic
                DoctorClinic.objects.create(
                    doctor=doctor,
                    clinic_id=clinic_id,
                    is_primary=True
                )

            messages.success(request, f'پزشک {user.get_full_name()} با موفقیت ایجاد شد')
        except Exception as e:
            messages.error(request, f'خطا در ایجاد پزشک: {str(e)}')

    return redirect('admin_doctors')


@superadmin_required
def admin_doctor_edit(request, doctor_id):
    """ویرایش پزشک"""
    from apps.doctors.models import Doctor, DoctorClinic
    from apps.clinics.models import Clinic

    doctor = get_object_or_404(Doctor.objects.select_related('user'), id=doctor_id)

    if request.method == 'POST':
        try:
            # بروزرسانی اطلاعات کاربر
            user = doctor.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.save()

            # بروزرسانی اطلاعات پزشک
            doctor.specialization = request.POST.get('specialization', doctor.specialization)
            doctor.medical_code = request.POST.get('medical_code', doctor.medical_code)
            doctor.visit_duration = int(request.POST.get('visit_duration', doctor.visit_duration))
            doctor.gap_between_visits = int(request.POST.get('gap_between_visits', doctor.gap_between_visits))
            doctor.max_daily_appointments = int(request.POST.get('max_daily_appointments', doctor.max_daily_appointments))
            doctor.bio = request.POST.get('bio', doctor.bio)
            doctor.save()

            messages.success(request, f'اطلاعات پزشک {user.get_full_name()} بروزرسانی شد')
        except Exception as e:
            messages.error(request, f'خطا در ویرایش پزشک: {str(e)}')
        return redirect('admin_doctors')

    clinics = Clinic.objects.filter(is_active=True)
    doctor_clinics = DoctorClinic.objects.filter(doctor=doctor).select_related('clinic')

    context = {
        'active_page': 'doctors',
        'doctor': doctor,
        'clinics': clinics,
        'doctor_clinics': doctor_clinics,
    }
    return render(request, 'admin_panel/doctor_edit.html', context)


@superadmin_required
def admin_doctor_detail(request, doctor_id):
    """جزئیات پزشک"""
    from apps.doctors.models import Doctor, DoctorClinic, WorkSchedule
    from apps.appointments.models import Appointment

    doctor = get_object_or_404(Doctor.objects.select_related('user'), id=doctor_id)
    today = timezone.now().date()

    doctor_clinics = DoctorClinic.objects.filter(doctor=doctor).select_related('clinic')
    schedules = WorkSchedule.objects.filter(doctor=doctor, is_active=True).select_related('clinic')
    today_appointments = Appointment.objects.filter(
        doctor=doctor, date=today
    ).exclude(status='cancelled').select_related('patient').order_by('time')

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='visited').count()

    context = {
        'active_page': 'doctors',
        'doctor': doctor,
        'doctor_clinics': doctor_clinics,
        'schedules': schedules,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'admin_panel/doctor_detail.html', context)


@superadmin_required
def admin_doctor_toggle(request, doctor_id):
    """فعال/غیرفعال کردن پزشک"""
    from apps.doctors.models import Doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    doctor.is_active = not doctor.is_active
    doctor.save()
    status = 'فعال' if doctor.is_active else 'غیرفعال'
    messages.success(request, f'پزشک {doctor.user.get_full_name()} {status} شد')
    return redirect('admin_doctors')


# =============================================================================
# مدیریت مراکز درمانی
# =============================================================================

@superadmin_required
def admin_clinics(request):
    """لیست مراکز"""
    from apps.clinics.models import Clinic
    from apps.doctors.models import DoctorClinic

    clinics = Clinic.objects.all().order_by('-created_at')
    for clinic in clinics:
        clinic.doctor_count = DoctorClinic.objects.filter(clinic=clinic).count()

    context = {
        'active_page': 'clinics',
        'clinics': clinics,
    }
    return render(request, 'admin_panel/clinics.html', context)


@superadmin_required
def admin_clinic_add(request):
    """افزودن مرکز"""
    from apps.clinics.models import Clinic

    if request.method == 'POST':
        try:
            Clinic.objects.create(
                name=request.POST.get('name', ''),
                province=request.POST.get('province', ''),
                city=request.POST.get('city', ''),
                address=request.POST.get('address', ''),
                phone=request.POST.get('phone', ''),
                postal_code=request.POST.get('postal_code', ''),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'مرکز درمانی با موفقیت ایجاد شد')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')

    return redirect('admin_clinics')


@superadmin_required
def admin_clinic_edit(request, clinic_id):
    """ویرایش مرکز درمانی"""
    from apps.clinics.models import Clinic

    clinic = get_object_or_404(Clinic, id=clinic_id)

    if request.method == 'POST':
        try:
            clinic.name = request.POST.get('name', clinic.name)
            clinic.province = request.POST.get('province', clinic.province)
            clinic.city = request.POST.get('city', clinic.city)
            clinic.address = request.POST.get('address', clinic.address)
            clinic.phone = request.POST.get('phone', clinic.phone)
            clinic.postal_code = request.POST.get('postal_code', clinic.postal_code)
            clinic.description = request.POST.get('description', clinic.description)
            clinic.save()
            messages.success(request, f'مرکز {clinic.name} بروزرسانی شد')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        return redirect('admin_clinics')

    context = {
        'active_page': 'clinics',
        'clinic': clinic,
    }
    return render(request, 'admin_panel/clinic_edit.html', context)


# =============================================================================
# مدیریت کاربران
# =============================================================================

@superadmin_required
def admin_users(request):
    """لیست کاربران"""
    from apps.accounts.models import User

    role_filter = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)

    # آمار نقش‌ها
    role_stats = User.objects.values('role').annotate(count=Count('id'))
    stats = {item['role']: item['count'] for item in role_stats}

    context = {
        'active_page': 'users',
        'users': users[:100],
        'doctor_count': stats.get('doctor', 0),
        'secretary_count': stats.get('secretary', 0),
        'patient_count': stats.get('patient', 0),
        'staff_count': stats.get('staff', 0),
        'current_role': role_filter,
    }
    return render(request, 'admin_panel/users.html', context)


@superadmin_required
def admin_user_edit(request, user_id):
    """ویرایش کاربر"""
    from apps.accounts.models import User

    edit_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            edit_user.first_name = request.POST.get('first_name', edit_user.first_name)
            edit_user.last_name = request.POST.get('last_name', edit_user.last_name)
            edit_user.phone = request.POST.get('phone', edit_user.phone)
            edit_user.email = request.POST.get('email', edit_user.email) or None
            edit_user.role = request.POST.get('role', edit_user.role)
            edit_user.save()
            messages.success(request, f'کاربر {edit_user.get_full_name()} بروزرسانی شد')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        return redirect('admin_users')

    context = {
        'active_page': 'users',
        'edit_user': edit_user,
    }
    return render(request, 'admin_panel/user_edit.html', context)


@superadmin_required
def admin_user_toggle(request, user_id):
    """فعال/غیرفعال کردن کاربر"""
    from apps.accounts.models import User
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'نمی‌توانید خودتان را غیرفعال کنید')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'فعال' if user.is_active else 'غیرفعال'
        messages.success(request, f'کاربر {user.get_full_name()} {status} شد')
    return redirect('admin_users')


@superadmin_required
def admin_user_add(request):
    """افزودن کاربر جدید (منشی، کارمند، بیمار، پزشک)"""
    from apps.accounts.models import User

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'patient')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip() or None
        national_code = request.POST.get('national_code', '').strip() or None

        # اعتبارسنجی
        if not phone or len(phone) != 11 or not phone.startswith('09'):
            messages.error(request, 'شماره موبایل معتبر نیست')
            return render(request, 'admin_panel/user_add.html', {'active_page': 'users'})

        if not first_name or not last_name:
            messages.error(request, 'نام و نام خانوادگی الزامی است')
            return render(request, 'admin_panel/user_add.html', {'active_page': 'users'})

        if not password or len(password) < 6:
            messages.error(request, 'رمز عبور باید حداقل ۶ کاراکتر باشد')
            return render(request, 'admin_panel/user_add.html', {'active_page': 'users'})

        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره موبایل قبلاً ثبت شده')
            return render(request, 'admin_panel/user_add.html', {'active_page': 'users'})

        try:
            user = User.objects.create_user(
                phone=phone,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                email=email,
                national_code=national_code,
            )

            # اگر پزشک است، پروفایل پزشک بساز
            if role == 'doctor':
                from apps.doctors.models import Doctor
                medical_code = request.POST.get('medical_code', '').strip()
                specialization = request.POST.get('specialization', '').strip()
                if medical_code and specialization:
                    Doctor.objects.create(
                        user=user,
                        medical_code=medical_code,
                        specialization=specialization,
                    )

            messages.success(request, f'کاربر «{user.get_full_name()}» با نقش «{user.get_role_display()}» ایجاد شد')
            return redirect('admin_users')
        except Exception as e:
            messages.error(request, f'خطا در ایجاد کاربر: {str(e)}')

    context = {
        'active_page': 'users',
    }
    return render(request, 'admin_panel/user_add.html', context)


# =============================================================================
# درگاه پرداخت
# =============================================================================

@superadmin_required
def admin_gateways(request):
    """تنظیمات درگاه پرداخت"""
    from django.conf import settings as django_settings

    context = {
        'active_page': 'gateways',
        'zarinpal_merchant': getattr(django_settings, 'ZARINPAL_MERCHANT_ID', ''),
        'zarinpal_sandbox': getattr(django_settings, 'ZARINPAL_SANDBOX', True),
        'drik_api_key': getattr(django_settings, 'DRIK_API_KEY', ''),
        'drik_sandbox': getattr(django_settings, 'DRIK_SANDBOX', True),
    }
    return render(request, 'admin_panel/gateways.html', context)


@superadmin_required
def admin_gateways_save(request):
    """ذخیره تنظیمات درگاه"""
    if request.method == 'POST':
        # TODO: ذخیره در .env یا database
        messages.success(request, 'تنظیمات درگاه پرداخت ذخیره شد')
    return redirect('admin_gateways')


# =============================================================================
# پلن‌ها
# =============================================================================

@superadmin_required
def admin_plans(request):
    """مدیریت پلن‌ها"""
    context = {
        'active_page': 'plans',
        'plans': [],  # TODO: لود از دیتابیس بعد از ایجاد مدل Plan
    }
    return render(request, 'admin_panel/plans.html', context)


@superadmin_required
def admin_plan_add(request):
    """افزودن پلن"""
    if request.method == 'POST':
        # TODO: ذخیره پلن
        messages.success(request, 'پلن جدید اضافه شد')
    return redirect('admin_plans')


@superadmin_required
def admin_plan_edit(request, plan_id):
    """ویرایش پلن"""
    messages.info(request, 'این بخش در حال توسعه است')
    return redirect('admin_plans')


# =============================================================================
# تراکنش‌ها
# =============================================================================

@superadmin_required
def admin_transactions(request):
    """لیست تراکنش‌ها"""
    from apps.payments.models import Transaction

    transactions = Transaction.objects.select_related(
        'user', 'appointment'
    ).order_by('-created_at')[:100]

    # آمار
    total_stats = Transaction.objects.aggregate(
        success=Count('id', filter=Q(status__in=['paid', 'verified'])),
        failed=Count('id', filter=Q(status='failed')),
        pending=Count('id', filter=Q(status='pending')),
        revenue=Sum('amount', filter=Q(status__in=['paid', 'verified'])),
    )

    context = {
        'active_page': 'transactions',
        'transactions': transactions,
        'success_count': total_stats['success'] or 0,
        'failed_count': total_stats['failed'] or 0,
        'pending_count': total_stats['pending'] or 0,
        'total_revenue': total_stats['revenue'] or 0,
    }
    return render(request, 'admin_panel/transactions.html', context)


# =============================================================================
# گزارش‌ها
# =============================================================================

@superadmin_required
def admin_reports(request):
    """صفحه گزارش‌ها"""
    from apps.accounts.models import User
    from apps.doctors.models import Doctor
    from apps.appointments.models import Appointment

    today = timezone.now().date()
    month_start = today.replace(day=1)

    context = {
        'active_page': 'reports',
        'total_patients': User.objects.filter(role='patient').count(),
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
        'active_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_appointments': Appointment.objects.count(),
        'completed_appointments': Appointment.objects.filter(status='visited').count(),
        'cancelled_appointments': Appointment.objects.filter(status='cancelled').count(),
    }
    return render(request, 'admin_panel/reports.html', context)


# =============================================================================
# لاگ سیستم
# =============================================================================

@superadmin_required
def admin_logs(request):
    """لاگ سیستم"""
    from apps.accounts.models import AuditLog

    logs = AuditLog.objects.select_related('user').order_by('-created_at')[:100]

    # تبدیل action به level برای نمایش آیکون مناسب
    for log in logs:
        log.level = {
            'create': 'success',
            'update': 'info',
            'delete': 'warning',
            'login': 'info',
            'logout': 'info',
            'password_change': 'warning',
            'other': 'info',
        }.get(log.action, 'info')
        log.message = f"{log.get_action_display()}: {log.object_repr or ''}"

    context = {
        'active_page': 'logs',
        'logs': logs,
    }
    return render(request, 'admin_panel/logs.html', context)


# =============================================================================
# تنظیمات
# =============================================================================

@superadmin_required
def admin_settings(request):
    """صفحه تنظیمات"""
    context = {
        'active_page': 'settings',
        'settings': {},  # TODO: لود از دیتابیس
    }
    return render(request, 'admin_panel/settings.html', context)


@superadmin_required
def admin_settings_save(request):
    """ذخیره تنظیمات"""
    if request.method == 'POST':
        section = request.POST.get('section', '')
        # TODO: ذخیره تنظیمات در دیتابیس
        messages.success(request, f'تنظیمات {section} ذخیره شد')
    return redirect('admin_settings')


# =============================================================================
# سرویس پیامک
# =============================================================================

@superadmin_required
def admin_sms(request):
    """مدیریت سرویس پیامک"""
    from apps.notifications.models import SMS

    recent_sms = SMS.objects.order_by('-created_at')[:20]

    context = {
        'active_page': 'sms',
        'recent_sms': recent_sms,
        'sms_api_key': '',  # TODO: لود از تنظیمات
    }
    return render(request, 'admin_panel/sms.html', context)


@superadmin_required
def admin_sms_save(request):
    """ذخیره تنظیمات پیامک"""
    if request.method == 'POST':
        messages.success(request, 'تنظیمات پیامک ذخیره شد')
    return redirect('admin_sms')


@superadmin_required
def admin_sms_templates_save(request):
    """ذخیره الگوهای پیامک"""
    if request.method == 'POST':
        messages.success(request, 'الگوهای پیامک ذخیره شد')
    return redirect('admin_sms')


# =============================================================================
# ویرایش مرکز درمانی
# =============================================================================

@superadmin_required
def admin_clinic_edit(request, clinic_id):
    """ویرایش مرکز درمانی"""
    from apps.clinics.models import Clinic

    clinic = get_object_or_404(Clinic, id=clinic_id)

    if request.method == 'POST':
        try:
            clinic.name = request.POST.get('name', clinic.name)
            clinic.province = request.POST.get('province', clinic.province)
            clinic.city = request.POST.get('city', clinic.city)
            clinic.address = request.POST.get('address', clinic.address)
            clinic.phone = request.POST.get('phone', clinic.phone)
            clinic.postal_code = request.POST.get('postal_code', clinic.postal_code)
            clinic.description = request.POST.get('description', clinic.description)
            clinic.save()
            messages.success(request, f'مرکز {clinic.name} بروزرسانی شد')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        return redirect('admin_clinics')

    context = {
        'active_page': 'clinics',
        'clinic': clinic,
    }
    return render(request, 'admin_panel/clinic_edit.html', context)


# =============================================================================
# ویرایش کاربر
# =============================================================================

@superadmin_required
def admin_user_edit(request, user_id):
    """ویرایش کاربر"""
    from apps.accounts.models import User

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone = request.POST.get('phone', user.phone)
            user.email = request.POST.get('email', user.email) or None
            new_role = request.POST.get('role', user.role)
            if new_role in dict(User.ROLE_CHOICES):
                user.role = new_role
            user.save()
            messages.success(request, f'کاربر {user.get_full_name()} بروزرسانی شد')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        return redirect('admin_users')

    context = {
        'active_page': 'users',
        'edit_user': user,
    }
    return render(request, 'admin_panel/user_edit.html', context)

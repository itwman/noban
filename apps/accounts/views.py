"""
Views برای اپلیکیشن accounts - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timedelta
from .models import User


def home(request):
    """صفحه اصلی سایت"""
    return render(request, 'home.html')


def login_view(request):
    """صفحه ورود"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        user = authenticate(request, username=phone, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'خوش آمدید {user.get_full_name()}')
            
            # هدایت بر اساس نقش
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """خروج از سیستم"""
    logout(request)
    messages.info(request, 'با موفقیت خارج شدید')
    return redirect('home')


@login_required
def dashboard(request):
    """داشبورد - هدایت به داشبورد مناسب بر اساس نقش"""
    user = request.user
    
    if user.role == 'superadmin':
        return superadmin_dashboard(request)
    elif user.role == 'doctor':
        return redirect('doctor_dashboard')
    elif user.role == 'secretary':
        return redirect('secretary_dashboard')
    elif user.role == 'staff':
        return staff_dashboard(request)
    else:  # patient
        return redirect('patient_dashboard')


def superadmin_dashboard(request):
    """داشبورد مدیر کل - ریدایرکت به پنل مدیریت"""
    return redirect('admin_dashboard')


def doctor_dashboard(request):
    """داشبورد پزشک"""
    from apps.doctors.models import Doctor
    from apps.appointments.models import Appointment
    
    user = request.user
    today = timezone.now().date()
    
    # دریافت اطلاعات پزشک
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        doctor = None
    
    context = {
        'doctor': doctor,
        'today_appointments': [],
        'today_appointments_count': 0,
        'visited_count': 0,
        'waiting_count': 0,
        'queue_count': 0,
        'current_patient': None,
        'recent_patients': [],
        'week_total': 0,
        'week_visited': 0,
        'week_cancelled': 0,
    }
    
    if doctor:
        # نوبت‌های امروز
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today
        ).exclude(
            status='cancelled'
        ).select_related('patient').order_by('time')
        
        context['today_appointments'] = today_appointments
        context['today_appointments_count'] = today_appointments.count()
        
        # آمار امروز
        context['visited_count'] = today_appointments.filter(status='visited').count()
        context['waiting_count'] = today_appointments.filter(
            status__in=['confirmed', 'pending']
        ).count()
        context['queue_count'] = today_appointments.filter(status='arrived').count()
        
        # بیمار فعلی (در حال ویزیت)
        current = today_appointments.filter(status='in_progress').first()
        if not current:
            # اگر کسی در حال ویزیت نیست، اولین بیمار حاضر را نشان بده
            current = today_appointments.filter(status='arrived').first()
        context['current_patient'] = current
        
        # آخرین بیماران
        recent_patient_ids = Appointment.objects.filter(
            doctor=doctor,
            status='visited'
        ).values('patient').annotate(
            visit_count=Count('id'),
            last_visit=Max('date')
        ).order_by('-last_visit')[:5]
        
        recent_patients = []
        for item in recent_patient_ids:
            try:
                patient = User.objects.get(id=item['patient'])
                patient.visit_count = item['visit_count']
                patient.last_visit = item['last_visit']
                recent_patients.append(patient)
            except User.DoesNotExist:
                pass
        
        context['recent_patients'] = recent_patients
        
        # آمار هفته
        week_start = today - timedelta(days=today.weekday())
        week_appointments = Appointment.objects.filter(
            doctor=doctor,
            date__gte=week_start,
            date__lte=today
        )
        
        context['week_total'] = week_appointments.exclude(status='cancelled').count()
        context['week_visited'] = week_appointments.filter(status='visited').count()
        context['week_cancelled'] = week_appointments.filter(status='cancelled').count()
    
    return render(request, 'dashboard/doctor.html', context)


def secretary_dashboard(request):
    """داشبورد منشی"""
    from apps.appointments.models import Appointment
    
    today = timezone.now().date()
    
    context = {
        'today_appointments': Appointment.objects.filter(
            date=today
        ).select_related('patient', 'doctor', 'doctor__user').order_by('time')[:20],
        'pending_count': Appointment.objects.filter(
            date=today, status='pending'
        ).count(),
    }
    
    return render(request, 'dashboard/secretary.html', context)


def staff_dashboard(request):
    """داشبورد کارمند"""
    return render(request, 'dashboard/staff.html')


def patient_dashboard(request):
    """داشبورد بیمار"""
    from apps.appointments.models import Appointment
    
    user = request.user
    today = timezone.now().date()
    
    # نوبت‌های آینده (پیش‌رو)
    appointments = Appointment.objects.filter(
        patient=user,
        date__gte=today,
        status__in=['pending', 'confirmed']
    ).select_related('doctor', 'doctor__user', 'clinic').order_by('date', 'time')[:5]
    
    # تعداد نوبت‌های پیش‌رو
    upcoming_count = appointments.count()
    
    # تعداد ویزیت‌های انجام شده
    completed_count = Appointment.objects.filter(
        patient=user,
        status='visited'
    ).count()
    
    # تعداد پرونده‌های پزشکی
    try:
        from apps.patients.models import MedicalRecord
        records_count = MedicalRecord.objects.filter(patient=user).count()
    except Exception:
        records_count = 0
    
    # تعداد پزشکان معالج (پزشکانی که بیمار نزدشان نوبت داشته)
    my_doctors_count = Appointment.objects.filter(
        patient=user
    ).values('doctor').distinct().count()
    
    # نوبت فعال (نزدیک‌ترین نوبت تأیید شده)
    active_appointment = Appointment.objects.filter(
        patient=user,
        date__gte=today,
        status='confirmed'
    ).select_related('doctor', 'doctor__user').order_by('date', 'time').first()
    
    # آخرین ویزیت‌ها
    recent_visits = Appointment.objects.filter(
        patient=user,
        status='visited'
    ).select_related('doctor', 'doctor__user').order_by('-date')[:5]
    
    context = {
        'appointments': appointments,
        'upcoming_appointments': upcoming_count,
        'upcoming_count': upcoming_count,
        'completed_appointments': completed_count,
        'medical_records': records_count,
        'my_doctors': my_doctors_count,
        'active_appointment': active_appointment,
        'recent_visits': recent_visits,
        'active_queue': None,
        'notifications_count': 0,
    }
    
    return render(request, 'dashboard/patient.html', context)


@login_required
def profile(request):
    """صفحه پروفایل کاربر"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.national_code = request.POST.get('national_code', user.national_code)
        user.address = request.POST.get('address', user.address)
        
        # آپلود تصویر پروفایل
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'پروفایل با موفقیت بروزرسانی شد')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html')


def register(request):
    """صفحه ثبت‌نام"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # دریافت اطلاعات از فرم
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'patient')
        national_code = request.POST.get('national_code', '').strip()
        
        # اعتبارسنجی
        errors = []
        
        # بررسی شماره موبایل
        if not phone or len(phone) != 11 or not phone.startswith('09'):
            errors.append('شماره موبایل معتبر نیست')
        
        # بررسی رمز عبور
        if len(password) < 8:
            errors.append('رمز عبور باید حداقل ۸ کاراکتر باشد')
        
        if password != password_confirm:
            errors.append('رمز عبور و تکرار آن مطابقت ندارند')
        
        # بررسی نام
        if not first_name or not last_name:
            errors.append('نام و نام خانوادگی الزامی است')
        
        # بررسی تکراری نبودن شماره موبایل
        if User.objects.filter(phone=phone).exists():
            errors.append('این شماره موبایل قبلاً ثبت شده است')
        
        # اگر پزشک است
        if role == 'doctor':
            medical_code = request.POST.get('medical_code', '').strip()
            specialization = request.POST.get('specialization', '').strip()
            
            if not medical_code:
                errors.append('کد نظام پزشکی الزامی است')
            if not specialization:
                errors.append('تخصص الزامی است')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html')
        
        try:
            # ایجاد کاربر
            user = User.objects.create_user(
                phone=phone,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                national_code=national_code if national_code else None,
            )
            
            # اگر پزشک است، اطلاعات پزشک را ذخیره کن
            if role == 'doctor':
                from apps.doctors.models import Doctor
                Doctor.objects.create(
                    user=user,
                    medical_code=request.POST.get('medical_code'),
                    specialization=request.POST.get('specialization'),
                )
            
            messages.success(request, f'{first_name} عزیز، ثبت‌نام شما با موفقیت انجام شد. لطفاً وارد شوید.')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.')
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
    
    return render(request, 'accounts/register.html')


def forgot_password(request):
    """صفحه فراموشی رمز عبور"""
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        if not phone or len(phone) != 11:
            messages.error(request, 'شماره موبایل معتبر نیست')
            return render(request, 'accounts/forgot_password.html')
        
        # بررسی وجود کاربر
        if not User.objects.filter(phone=phone).exists():
            messages.error(request, 'کاربری با این شماره موبایل یافت نشد')
            return render(request, 'accounts/forgot_password.html')
        
        # TODO: ارسال کد تأیید با SMS
        # فعلاً به صفحه تأیید کد هدایت می‌کنیم
        request.session['reset_phone'] = phone
        messages.info(request, 'کد تأیید به شماره موبایل شما ارسال شد')
        return redirect('verify_code')
    
    return render(request, 'accounts/forgot_password.html')


def verify_code(request):
    """صفحه تأیید کد"""
    phone = request.session.get('reset_phone')
    
    if not phone:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        # TODO: بررسی کد تأیید
        # فعلاً هر کدی قبول می‌شود
        if code and len(code) >= 4:
            request.session['verified_phone'] = phone
            return redirect('reset_password')
        else:
            messages.error(request, 'کد تأیید نامعتبر است')
    
    return render(request, 'accounts/verify_code.html', {'phone': phone})


def reset_password(request):
    """صفحه تنظیم رمز عبور جدید"""
    phone = request.session.get('verified_phone')
    
    if not phone:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        if len(password) < 8:
            messages.error(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد')
        elif password != password_confirm:
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند')
        else:
            try:
                user = User.objects.get(phone=phone)
                user.set_password(password)
                user.save()
                
                # پاک کردن session
                del request.session['reset_phone']
                del request.session['verified_phone']
                
                messages.success(request, 'رمز عبور با موفقیت تغییر کرد. لطفاً وارد شوید.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'کاربر یافت نشد')
    
    return render(request, 'accounts/reset_password.html')


@login_required
def change_password(request):
    """تغییر رمز عبور"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'رمز عبور فعلی اشتباه است')
        elif new_password != confirm_password:
            messages.error(request, 'رمز عبور جدید با تکرار آن مطابقت ندارد')
        elif len(new_password) < 8:
            messages.error(request, 'رمز عبور باید حداقل 8 کاراکتر باشد')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'رمز عبور با موفقیت تغییر کرد. لطفاً دوباره وارد شوید.')
            return redirect('login')
    
    return render(request, 'accounts/change_password.html')

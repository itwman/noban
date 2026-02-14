"""
Views برای بخش پزشکان - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import (
    Doctor, WorkSchedule, DoctorHoliday, DoctorClinic,
    ServiceType, InsuranceType, DoctorTariff
)
from .services.tariff_service import TariffService
from apps.appointments.models import Appointment
from apps.accounts.models import User
from apps.patients.models import MedicalRecord, MedicalTerm, PrescriptionItem
from apps.clinics.models import Clinic
import json


def doctor_list(request):
    """لیست پزشکان"""
    doctors = Doctor.objects.filter(is_active=True).select_related('user')
    
    # فیلتر تخصص
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    # جستجو
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(
            user__first_name__icontains=search
        ) | doctors.filter(
            user__last_name__icontains=search
        )
    
    specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
    
    context = {
        'doctors': doctors,
        'specializations': specializations,
    }
    return render(request, 'doctors/list.html', context)


def doctor_detail(request, pk):
    """جزئیات پزشک"""
    doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/detail.html', context)


# ===== پنل پزشک =====

def get_doctor_or_404(request):
    """دریافت پزشک مرتبط با کاربر فعلی"""
    return get_object_or_404(Doctor, user=request.user)


@login_required
def doctor_dashboard(request):
    """داشبورد پزشک"""
    doctor = get_doctor_or_404(request)
    today = timezone.now().date()
    
    # آمار امروز
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today
    )
    
    today_count = today_appointments.count()
    visited_today = today_appointments.filter(status='visited').count()
    waiting_today = today_appointments.filter(status__in=['confirmed', 'arrived']).count()
    
    # آمار هفته
    week_start = today - timedelta(days=today.weekday())
    week_appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=week_start,
        date__lte=today
    )
    week_visited = week_appointments.filter(status='visited').count()
    
    # آمار ماه
    month_start = today.replace(day=1)
    month_appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=month_start,
        date__lte=today
    )
    month_visited = month_appointments.filter(status='visited').count()
    
    # نوبت‌های آینده امروز
    upcoming = today_appointments.filter(
        status__in=['pending', 'confirmed', 'arrived']
    ).order_by('time')[:5]
    
    # بیمار فعلی
    current_patient = today_appointments.filter(status='in_progress').first()
    
    # مراکز پزشک
    clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')[:3]
    
    context = {
        'doctor': doctor,
        'today': today,
        'today_count': today_count,
        'visited_today': visited_today,
        'waiting_today': waiting_today,
        'week_visited': week_visited,
        'month_visited': month_visited,
        'upcoming_appointments': upcoming,
        'current_patient': current_patient,
        'clinics': clinics,
    }
    return render(request, 'dashboard/doctor.html', context)


@login_required
def doctor_today_appointments(request):
    """نوبت‌های امروز پزشک"""
    doctor = get_doctor_or_404(request)
    today = timezone.now().date()
    
    # همه نوبت‌های امروز برای آمار
    all_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today
    ).select_related('patient', 'clinic')
    
    # آمار
    total_count = all_appointments.count()
    visited_count = all_appointments.filter(status='visited').count()
    arrived_count = all_appointments.filter(status__in=['arrived', 'in_progress']).count()
    confirmed_count = all_appointments.filter(status='confirmed').count()
    pending_count = all_appointments.filter(status='pending').count()
    
    # فیلتر وضعیت برای نمایش
    appointments = all_appointments.order_by('time')
    status = request.GET.get('status')
    if status and status != 'all':
        appointments = appointments.filter(status=status)
    
    context = {
        'appointments': appointments,
        'doctor': doctor,
        'today': today,
        'total_count': total_count,
        'visited_count': visited_count,
        'arrived_count': arrived_count,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
    }
    return render(request, 'doctors/today_appointments.html', context)


@login_required
def doctor_schedule(request):
    """تقویم کاری پزشک"""
    doctor = get_doctor_or_404(request)
    
    # مراکز پزشک
    clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')
    
    # فیلتر بر اساس مرکز
    selected_clinic = request.GET.get('clinic')
    
    schedules = WorkSchedule.objects.filter(
        doctor=doctor
    ).select_related('clinic').order_by('day_of_week', 'start_time')
    
    if selected_clinic:
        schedules = schedules.filter(clinic_id=selected_clinic)
    
    if request.method == 'POST':
        # ذخیره تنظیمات ساعت کاری
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        clinic_id = request.POST.get('clinic')
        
        if day_of_week and start_time and end_time:
            # بررسی تداخل زمانی
            existing = WorkSchedule.objects.filter(
                doctor=doctor,
                day_of_week=int(day_of_week),
                clinic_id=clinic_id if clinic_id else None
            ).first()
            
            if existing:
                # بروزرسانی موجود
                existing.start_time = start_time
                existing.end_time = end_time
                existing.is_active = True
                existing.save()
            else:
                # ایجاد جدید
                WorkSchedule.objects.create(
                    doctor=doctor,
                    day_of_week=int(day_of_week),
                    start_time=start_time,
                    end_time=end_time,
                    clinic_id=clinic_id if clinic_id else None,
                    is_active=True,
                )
            
            messages.success(request, 'ساعت کاری با موفقیت ذخیره شد')
            return redirect('doctor_schedule')
    
    # لیست روزهای هفته
    days = [
        (0, 'شنبه'),
        (1, 'یکشنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنج‌شنبه'),
        (6, 'جمعه'),
    ]
    
    # تبدیل schedules به لیست برای استفاده در قالب
    schedules_list = list(schedules)
    
    context = {
        'schedules': schedules_list,
        'doctor': doctor,
        'days': days,
        'clinics': clinics,
        'selected_clinic': int(selected_clinic) if selected_clinic else None,
    }
    return render(request, 'doctors/schedule.html', context)


# ===== مدیریت مراکز پزشک =====

@login_required
def doctor_clinics(request):
    """لیست مراکز پزشک"""
    doctor = get_doctor_or_404(request)
    
    # مراکز متصل به پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor
    ).select_related('clinic').order_by('-is_primary', 'clinic__name')
    
    context = {
        'doctor': doctor,
        'doctor_clinics': doctor_clinics,
    }
    return render(request, 'doctors/clinics.html', context)


@login_required
def doctor_add_clinic(request):
    """افزودن مرکز جدید"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        clinic_type = request.POST.get('clinic_type')
        name = request.POST.get('name')
        province = request.POST.get('province')
        city = request.POST.get('city')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        if name and province and city and address:
            # ایجاد مرکز جدید
            clinic = Clinic.objects.create(
                clinic_type=clinic_type or 'office',
                name=name,
                province=province,
                city=city,
                address=address,
                phone=phone or '',
                owner=request.user,
                is_active=True,
            )
            
            # اتصال به پزشک
            is_primary = not DoctorClinic.objects.filter(doctor=doctor).exists()
            DoctorClinic.objects.create(
                doctor=doctor,
                clinic=clinic,
                is_primary=is_primary,
                is_active=True,
            )
            
            messages.success(request, f'{clinic.get_clinic_type_display()} "{name}" با موفقیت اضافه شد')
            return redirect('doctor_clinics')
        else:
            messages.error(request, 'لطفاً تمام فیلدهای ضروری را پر کنید')
    
    # لیست استان‌ها
    provinces = [
        'آذربایجان شرقی', 'آذربایجان غربی', 'اردبیل', 'اصفهان', 'البرز',
        'ایلام', 'بوشهر', 'تهران', 'چهارمحال و بختیاری', 'خراسان جنوبی',
        'خراسان رضوی', 'خراسان شمالی', 'خوزستان', 'زنجان', 'سمنان',
        'سیستان و بلوچستان', 'فارس', 'قزوین', 'قم', 'کردستان',
        'کرمان', 'کرمانشاه', 'کهگیلویه و بویراحمد', 'گلستان', 'گیلان',
        'لرستان', 'مازندران', 'مرکزی', 'هرمزگان', 'همدان', 'یزد'
    ]
    
    context = {
        'doctor': doctor,
        'provinces': provinces,
        'clinic_types': Clinic.CLINIC_TYPES,
    }
    return render(request, 'doctors/add_clinic.html', context)


@login_required
def doctor_edit_clinic(request, clinic_id):
    """ویرایش مرکز"""
    doctor = get_doctor_or_404(request)
    
    # بررسی دسترسی
    doctor_clinic = get_object_or_404(
        DoctorClinic,
        doctor=doctor,
        clinic_id=clinic_id
    )
    clinic = doctor_clinic.clinic
    
    # فقط مالک می‌تواند مرکز را ویرایش کند
    if clinic.owner != request.user:
        messages.error(request, 'شما اجازه ویرایش این مرکز را ندارید')
        return redirect('doctor_clinics')
    
    if request.method == 'POST':
        clinic.clinic_type = request.POST.get('clinic_type', clinic.clinic_type)
        clinic.name = request.POST.get('name', clinic.name)
        clinic.province = request.POST.get('province', clinic.province)
        clinic.city = request.POST.get('city', clinic.city)
        clinic.address = request.POST.get('address', clinic.address)
        clinic.phone = request.POST.get('phone', clinic.phone)
        clinic.description = request.POST.get('description', '')
        clinic.save()
        
        # به‌روزرسانی DoctorClinic
        doctor_clinic.room_number = request.POST.get('room_number', '')
        doctor_clinic.custom_visit_fee = request.POST.get('custom_visit_fee') or None
        doctor_clinic.save()
        
        messages.success(request, 'مرکز با موفقیت ویرایش شد')
        return redirect('doctor_clinics')
    
    # لیست استان‌ها
    provinces = [
        'آذربایجان شرقی', 'آذربایجان غربی', 'اردبیل', 'اصفهان', 'البرز',
        'ایلام', 'بوشهر', 'تهران', 'چهارمحال و بختیاری', 'خراسان جنوبی',
        'خراسان رضوی', 'خراسان شمالی', 'خوزستان', 'زنجان', 'سمنان',
        'سیستان و بلوچستان', 'فارس', 'قزوین', 'قم', 'کردستان',
        'کرمان', 'کرمانشاه', 'کهگیلویه و بویراحمد', 'گلستان', 'گیلان',
        'لرستان', 'مازندران', 'مرکزی', 'هرمزگان', 'همدان', 'یزد'
    ]
    
    context = {
        'doctor': doctor,
        'clinic': clinic,
        'doctor_clinic': doctor_clinic,
        'provinces': provinces,
        'clinic_types': Clinic.CLINIC_TYPES,
    }
    return render(request, 'doctors/edit_clinic.html', context)


@login_required
@require_POST
def doctor_delete_clinic(request, clinic_id):
    """حذف مرکز از لیست پزشک"""
    doctor = get_doctor_or_404(request)
    
    doctor_clinic = get_object_or_404(
        DoctorClinic,
        doctor=doctor,
        clinic_id=clinic_id
    )
    
    clinic_name = doctor_clinic.clinic.name
    
    # اگر مالک است، کل مرکز را حذف کن
    if doctor_clinic.clinic.owner == request.user:
        doctor_clinic.clinic.delete()  # Cascade حذف می‌شود
        messages.success(request, f'مرکز "{clinic_name}" حذف شد')
    else:
        # فقط اتصال را حذف کن
        doctor_clinic.delete()
        messages.success(request, f'از مرکز "{clinic_name}" خارج شدید')
    
    return redirect('doctor_clinics')


@login_required
@require_POST
def doctor_set_primary_clinic(request, clinic_id):
    """تنظیم مرکز اصلی"""
    doctor = get_doctor_or_404(request)
    
    # ابتدا همه را غیر اصلی کن
    DoctorClinic.objects.filter(doctor=doctor).update(is_primary=False)
    
    # سپس این را اصلی کن
    doctor_clinic = get_object_or_404(
        DoctorClinic,
        doctor=doctor,
        clinic_id=clinic_id
    )
    doctor_clinic.is_primary = True
    doctor_clinic.save()
    
    messages.success(request, f'"{doctor_clinic.clinic.name}" به عنوان مرکز اصلی تنظیم شد')
    return redirect('doctor_clinics')


@login_required
def doctor_link_clinic(request):
    """اتصال به مرکز موجود (بیمارستان/کلینیک)"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        clinic_id = request.POST.get('clinic_id')
        room_number = request.POST.get('room_number', '')
        
        if clinic_id:
            clinic = get_object_or_404(Clinic, id=clinic_id, is_active=True)
            
            # بررسی اتصال قبلی
            if DoctorClinic.objects.filter(doctor=doctor, clinic=clinic).exists():
                messages.error(request, 'شما قبلاً به این مرکز متصل شده‌اید')
            else:
                DoctorClinic.objects.create(
                    doctor=doctor,
                    clinic=clinic,
                    room_number=room_number,
                    is_active=True,
                )
                messages.success(request, f'به "{clinic.name}" متصل شدید')
                return redirect('doctor_clinics')
    
    # لیست مراکز عمومی که پزشک به آنها متصل نیست
    linked_clinic_ids = DoctorClinic.objects.filter(
        doctor=doctor
    ).values_list('clinic_id', flat=True)
    
    available_clinics = Clinic.objects.filter(
        is_active=True,
        is_public=True,
        clinic_type__in=['clinic', 'hospital', 'center']
    ).exclude(id__in=linked_clinic_ids)
    
    # جستجو
    search = request.GET.get('search', '')
    if search:
        available_clinics = available_clinics.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search)
        )
    
    context = {
        'doctor': doctor,
        'available_clinics': available_clinics,
        'search': search,
    }
    return render(request, 'doctors/link_clinic.html', context)


@login_required
def doctor_patients(request):
    """لیست بیماران پزشک"""
    doctor = get_doctor_or_404(request)
    
    # بیماران با تعداد مراجعه
    patient_stats = Appointment.objects.filter(
        doctor=doctor,
        status='visited'
    ).values('patient').annotate(
        visit_count=Count('id')
    ).order_by('-visit_count')
    
    patients = []
    for stat in patient_stats:
        try:
            patient = User.objects.get(id=stat['patient'])
            patient.visit_count = stat['visit_count']
            
            # آخرین مراجعه
            last_apt = Appointment.objects.filter(
                doctor=doctor,
                patient=patient,
                status='visited'
            ).order_by('-date').first()
            patient.last_visit = last_apt.date if last_apt else None
            
            patients.append(patient)
        except User.DoesNotExist:
            pass
    
    # جستجو
    search = request.GET.get('search')
    if search:
        patients = [p for p in patients if search in p.get_full_name() or search in p.phone]
    
    context = {
        'patients': patients,
        'doctor': doctor,
    }
    return render(request, 'doctors/patients.html', context)


@login_required
def doctor_patient_record(request, patient_id):
    """پرونده بیمار"""
    doctor = get_doctor_or_404(request)
    patient = get_object_or_404(User, id=patient_id)
    
    # بررسی دسترسی - فقط بیمارانی که نزد این پزشک نوبت داشته‌اند
    has_appointment = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).exists()
    
    if not has_appointment:
        messages.error(request, 'شما دسترسی به پرونده این بیمار را ندارید')
        return redirect('doctor_patients')
    
    # سوابق پزشکی (همراه آیتم‌های تجویز)
    records = MedicalRecord.objects.filter(
        doctor=doctor,
        patient=patient
    ).prefetch_related('prescription_items').order_by('-created_at')
    
    # نوبت‌های بیمار نزد این پزشک
    appointments = Appointment.objects.filter(
        doctor=doctor,
        patient=patient
    ).order_by('-date')
    
    context = {
        'patient': patient,
        'doctor': doctor,
        'records': records,
        'appointments': appointments,
    }
    return render(request, 'doctors/patient_record.html', context)


@login_required
def doctor_records(request):
    """همه پرونده‌های پزشک"""
    doctor = get_doctor_or_404(request)
    
    records = MedicalRecord.objects.filter(
        doctor=doctor
    ).select_related('patient', 'appointment').prefetch_related('prescription_items').order_by('-created_at')
    
    # جستجو
    search = request.GET.get('search')
    if search:
        records = records.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(diagnosis__icontains=search)
        )
    
    context = {
        'records': records,
        'doctor': doctor,
    }
    return render(request, 'doctors/records.html', context)


@login_required
def doctor_add_record(request, appointment_id):
    """ثبت پرونده برای نوبت"""
    doctor = get_doctor_or_404(request)
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        doctor=doctor
    )
    
    if request.method == 'POST':
        record = MedicalRecord.objects.create(
            doctor=doctor,
            patient=appointment.patient,
            appointment=appointment,
            visit_date=appointment.date or timezone.now().date(),
            chief_complaint=request.POST.get('chief_complaint', ''),
            diagnosis=request.POST.get('diagnosis', ''),
            prescription=request.POST.get('prescription', ''),
            notes=request.POST.get('notes', ''),
            next_visit_date=request.POST.get('next_visit_date') or None,
        )
        
        # ذخیره آیتم‌های تجویز (دارو، آزمایش، تصویربرداری، اقدام)
        prescription_data = request.POST.get('prescription_items_json', '[]')
        try:
            items = json.loads(prescription_data)
            for idx, item in enumerate(items):
                PrescriptionItem.objects.create(
                    record=record,
                    item_type=item.get('item_type', 'medication'),
                    name=item.get('name', ''),
                    name_en=item.get('name_en', '') or None,
                    form=item.get('form', '') or None,
                    dosage=item.get('dosage', '') or None,
                    frequency=item.get('frequency', '') or None,
                    frequency_custom=item.get('frequency_custom', '') or None,
                    timing=item.get('timing', '') or None,
                    duration_value=int(item['duration_value']) if item.get('duration_value') else None,
                    duration_unit=item.get('duration_unit', '') or None,
                    quantity=item.get('quantity', '') or None,
                    instructions=item.get('instructions', '') or None,
                    sort_order=idx,
                )
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        
        messages.success(request, 'پرونده با موفقیت ثبت شد')
        return redirect('doctor_patient_record', patient_id=appointment.patient.id)
    
    context = {
        'appointment': appointment,
        'doctor': doctor,
    }
    return render(request, 'doctors/add_record.html', context)


@login_required
def doctor_new_record(request):
    """ثبت پرونده جدید بدون نوبت"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        patient = get_object_or_404(User, id=patient_id)
        
        record = MedicalRecord.objects.create(
            doctor=doctor,
            patient=patient,
            visit_date=timezone.now().date(),
            chief_complaint=request.POST.get('chief_complaint', ''),
            diagnosis=request.POST.get('diagnosis', ''),
            prescription=request.POST.get('prescription', ''),
            notes=request.POST.get('notes', ''),
            next_visit_date=request.POST.get('next_visit_date') or None,
        )
        
        # ذخیره آیتم‌های تجویز
        prescription_data = request.POST.get('prescription_items_json', '[]')
        try:
            items = json.loads(prescription_data)
            for idx, item in enumerate(items):
                PrescriptionItem.objects.create(
                    record=record,
                    item_type=item.get('item_type', 'medication'),
                    name=item.get('name', ''),
                    name_en=item.get('name_en', '') or None,
                    form=item.get('form', '') or None,
                    dosage=item.get('dosage', '') or None,
                    frequency=item.get('frequency', '') or None,
                    frequency_custom=item.get('frequency_custom', '') or None,
                    timing=item.get('timing', '') or None,
                    duration_value=int(item['duration_value']) if item.get('duration_value') else None,
                    duration_unit=item.get('duration_unit', '') or None,
                    quantity=item.get('quantity', '') or None,
                    instructions=item.get('instructions', '') or None,
                    sort_order=idx,
                )
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        
        messages.success(request, 'پرونده با موفقیت ثبت شد')
        return redirect('doctor_patient_record', patient_id=patient.id)
    
    # لیست بیماران پزشک
    patient_ids = Appointment.objects.filter(
        doctor=doctor
    ).values_list('patient', flat=True).distinct()
    patients = User.objects.filter(id__in=patient_ids)
    
    context = {
        'patients': patients,
        'doctor': doctor,
    }
    return render(request, 'doctors/new_record.html', context)


@login_required
def doctor_live_queue(request):
    """صف زنده پزشک"""
    doctor = get_doctor_or_404(request)
    today = timezone.now().date()
    
    appointments = Appointment.objects.filter(
        doctor=doctor,
        date=today
    ).exclude(
        status__in=['cancelled', 'no_show']
    ).select_related('patient').order_by('queue_number', 'time')
    
    # بیمار فعلی
    current = appointments.filter(status='in_progress').first()
    if not current:
        current = appointments.filter(status='arrived').first()
    
    context = {
        'appointments': appointments,
        'doctor': doctor,
        'current_patient': current,
        'today': today,
    }
    return render(request, 'doctors/live_queue.html', context)


@login_required
def doctor_reports(request):
    """گزارش‌های پزشک"""
    doctor = get_doctor_or_404(request)
    today = timezone.now().date()
    
    # بازه زمانی
    period = request.GET.get('period', 'week')
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=7)
    
    appointments = Appointment.objects.filter(
        doctor=doctor,
        date__gte=start_date,
        date__lte=today
    )
    
    context = {
        'doctor': doctor,
        'total_appointments': appointments.count(),
        'visited_count': appointments.filter(status='visited').count(),
        'cancelled_count': appointments.filter(status='cancelled').count(),
        'no_show_count': appointments.filter(status='no_show').count(),
        'period': period,
        'start_date': start_date,
        'end_date': today,
    }
    return render(request, 'doctors/reports.html', context)


@login_required
def doctor_holidays(request):
    """مرخصی‌های پزشک"""
    doctor = get_doctor_or_404(request)
    
    holidays = DoctorHoliday.objects.filter(
        doctor=doctor
    ).order_by('-date')
    
    context = {
        'holidays': holidays,
        'doctor': doctor,
    }
    return render(request, 'doctors/holidays.html', context)


@login_required
def doctor_add_holiday(request):
    """افزودن مرخصی"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        reason = request.POST.get('reason', '')
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # بررسی تکراری نبودن
                if DoctorHoliday.objects.filter(doctor=doctor, date=date).exists():
                    messages.error(request, 'این تاریخ قبلاً به عنوان مرخصی ثبت شده است')
                else:
                    DoctorHoliday.objects.create(
                        doctor=doctor,
                        date=date,
                        reason=reason
                    )
                    messages.success(request, 'مرخصی با موفقیت ثبت شد')
                    return redirect('doctor_holidays')
            except ValueError:
                messages.error(request, 'تاریخ نامعتبر است')
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/add_holiday.html', context)


@login_required
def doctor_add_appointment(request):
    """ثبت نوبت جدید توسط پزشک"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        patient_phone = request.POST.get('patient_phone')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        
        # پیدا کردن یا ایجاد بیمار
        try:
            patient = User.objects.get(phone=patient_phone)
        except User.DoesNotExist:
            # ایجاد بیمار جدید
            first_name = request.POST.get('first_name', 'بیمار')
            last_name = request.POST.get('last_name', 'جدید')
            
            patient = User.objects.create(
                phone=patient_phone,
                first_name=first_name,
                last_name=last_name,
                role='patient',
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
            
            # محاسبه شماره صف
            last_queue = Appointment.objects.filter(
                doctor=doctor,
                date=date
            ).exclude(status='cancelled').order_by('-queue_number').first()
            
            queue_number = (last_queue.queue_number + 1) if last_queue else 1
            
            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date=date,
                time=time,
                queue_number=queue_number,
                status='confirmed',
            )
            
            messages.success(request, f'نوبت برای {patient.get_full_name()} با موفقیت ثبت شد')
            return redirect('doctor_today_appointments')
            
        except ValueError:
            messages.error(request, 'تاریخ یا ساعت نامعتبر است')
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/add_appointment.html', context)


@login_required
def doctor_settings(request):
    """تنظیمات پزشک"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        doctor.visit_duration = int(request.POST.get('visit_duration', 15))
        doctor.gap_between_visits = int(request.POST.get('gap_between_visits', 5))
        doctor.max_daily_appointments = int(request.POST.get('max_daily_appointments', 30))
        doctor.visit_fee = int(request.POST.get('visit_fee', 0))
        doctor.bio = request.POST.get('bio', '')
        
        if 'profile_image' in request.FILES:
            doctor.profile_image = request.FILES['profile_image']
        
        doctor.save()
        messages.success(request, 'تنظیمات با موفقیت ذخیره شد')
        return redirect('doctor_settings')
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/settings.html', context)


@login_required
@require_POST
def doctor_delete_schedule(request):
    """حذف برنامه کاری"""
    doctor = get_doctor_or_404(request)
    schedule_id = request.POST.get('schedule_id')
    
    try:
        schedule = WorkSchedule.objects.get(id=schedule_id, doctor=doctor)
        schedule.delete()
        messages.success(request, 'برنامه با موفقیت حذف شد')
    except WorkSchedule.DoesNotExist:
        messages.error(request, 'برنامه یافت نشد')
    
    return redirect('doctor_schedule')


# ===== مدیریت تعرفه‌ها =====

@login_required
def doctor_tariffs(request):
    """صفحه مدیریت تعرفه‌های پزشک"""
    doctor = get_doctor_or_404(request)
    
    # مراکز پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')
    
    # فیلتر مرکز
    selected_clinic = request.GET.get('clinic', '')
    
    # تعرفه‌های گروه‌بندی شده بر اساس مرکز
    grouped_tariffs = TariffService.get_tariffs_grouped_by_clinic(doctor.id)
    
    # اگر فیلتر مرکز فعال باشد
    if selected_clinic:
        if selected_clinic == 'general':
            # فقط تعرفه عمومی
            grouped_tariffs = {k: v for k, v in grouped_tariffs.items() if k is None}
        else:
            try:
                clinic_id = int(selected_clinic)
                grouped_tariffs = {
                    k: v for k, v in grouped_tariffs.items()
                    if k == clinic_id or k is None
                }
            except (ValueError, TypeError):
                pass
    
    # انواع خدمات و بیمه‌ها (برای فرم)
    services = ServiceType.objects.filter(is_active=True).order_by('sort_order')
    insurances = InsuranceType.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'doctor': doctor,
        'grouped_tariffs': grouped_tariffs,
        'doctor_clinics': doctor_clinics,
        'services': services,
        'insurances': insurances,
        'selected_clinic': selected_clinic,
    }
    return render(request, 'doctors/tariffs.html', context)


@login_required
def doctor_add_tariff(request):
    """افزودن تعرفه جدید"""
    doctor = get_doctor_or_404(request)
    
    if request.method == 'POST':
        clinic_id = request.POST.get('clinic_id') or None
        service_type_id = request.POST.get('service_type')
        insurance_type_id = request.POST.get('insurance_type')
        fee = request.POST.get('fee', '0').replace(',', '')
        deposit_required = request.POST.get('deposit_required') == 'on'
        deposit_type = request.POST.get('deposit_type', 'fixed')
        deposit_amount = request.POST.get('deposit_amount', '0').replace(',', '') or '0'
        deposit_percent = request.POST.get('deposit_percent', '0') or '0'
        online_payment_required = request.POST.get('online_payment_required') == 'on'
        description = request.POST.get('description', '')
        is_general = request.POST.get('is_general') == 'on'
        
        if is_general:
            clinic_id = None
        
        if service_type_id and insurance_type_id and fee:
            # بررسی تکراری نبودن
            exists = DoctorTariff.objects.filter(
                doctor=doctor,
                clinic_id=clinic_id,
                service_type_id=service_type_id,
                insurance_type_id=insurance_type_id
            ).exists()
            
            if exists:
                messages.error(request, 'تعرفه‌ای با این ترکیب قبلاً ثبت شده است')
            else:
                DoctorTariff.objects.create(
                    doctor=doctor,
                    clinic_id=clinic_id,
                    service_type_id=service_type_id,
                    insurance_type_id=insurance_type_id,
                    fee=int(fee or 0),
                    deposit_required=deposit_required,
                    deposit_amount=int(deposit_amount) if deposit_type == 'fixed' else 0,
                    deposit_percent=int(deposit_percent) if deposit_type == 'percent' else 0,
                    online_payment_required=online_payment_required,
                    description=description,
                    is_active=True,
                )
                messages.success(request, 'تعرفه با موفقیت اضافه شد')
                return redirect('doctor_tariffs')
        else:
            messages.error(request, 'لطفاً تمام فیلدهای الزامی را پر کنید')
    
    # مراکز پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')
    
    services = ServiceType.objects.filter(is_active=True).order_by('sort_order')
    insurances = InsuranceType.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'doctor': doctor,
        'doctor_clinics': doctor_clinics,
        'services': services,
        'insurances': insurances,
    }
    return render(request, 'doctors/add_tariff.html', context)


@login_required
def doctor_edit_tariff(request, tariff_id):
    """ویرایش تعرفه"""
    doctor = get_doctor_or_404(request)
    tariff = get_object_or_404(DoctorTariff, id=tariff_id, doctor=doctor)
    
    if request.method == 'POST':
        fee = request.POST.get('fee', '0').replace(',', '')
        deposit_required = request.POST.get('deposit_required') == 'on'
        deposit_type = request.POST.get('deposit_type', 'fixed')
        deposit_amount = request.POST.get('deposit_amount', '0').replace(',', '') or '0'
        deposit_percent = request.POST.get('deposit_percent', '0') or '0'
        online_payment_required = request.POST.get('online_payment_required') == 'on'
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        tariff.fee = int(fee or 0)
        tariff.deposit_required = deposit_required
        tariff.deposit_amount = int(deposit_amount) if deposit_type == 'fixed' else 0
        tariff.deposit_percent = int(deposit_percent) if deposit_type == 'percent' else 0
        tariff.online_payment_required = online_payment_required
        tariff.description = description
        tariff.is_active = is_active
        tariff.save()
        
        messages.success(request, 'تعرفه با موفقیت ویرایش شد')
        return redirect('doctor_tariffs')
    
    # مراکز پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')
    
    services = ServiceType.objects.filter(is_active=True).order_by('sort_order')
    insurances = InsuranceType.objects.filter(is_active=True).order_by('sort_order')
    
    context = {
        'doctor': doctor,
        'tariff': tariff,
        'doctor_clinics': doctor_clinics,
        'services': services,
        'insurances': insurances,
    }
    return render(request, 'doctors/edit_tariff.html', context)


@login_required
@require_POST
def doctor_delete_tariff(request, tariff_id):
    """حذف تعرفه"""
    doctor = get_doctor_or_404(request)
    tariff = get_object_or_404(DoctorTariff, id=tariff_id, doctor=doctor)
    
    tariff.delete()
    messages.success(request, 'تعرفه با موفقیت حذف شد')
    return redirect('doctor_tariffs')


@login_required
def doctor_bulk_tariffs(request):
    """تنظیم دسته‌ای تعرفه‌ها (ماتریس)"""
    doctor = get_doctor_or_404(request)
    
    # مراکز پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic')
    
    services = ServiceType.objects.filter(is_active=True).order_by('sort_order')
    insurances = InsuranceType.objects.filter(is_active=True).order_by('sort_order')
    
    # مرکز انتخاب شده
    selected_clinic_id = request.GET.get('clinic', '')
    
    # تعرفه‌های موجود برای پر کردن ماتریس
    existing_tariffs = {}
    tariff_qs = DoctorTariff.objects.filter(doctor=doctor)
    
    if selected_clinic_id:
        if selected_clinic_id == 'general':
            tariff_qs = tariff_qs.filter(clinic_id__isnull=True)
            selected_clinic_id_int = None
        else:
            try:
                selected_clinic_id_int = int(selected_clinic_id)
                tariff_qs = tariff_qs.filter(
                    Q(clinic_id=selected_clinic_id_int) | Q(clinic_id__isnull=True)
                )
            except (ValueError, TypeError):
                selected_clinic_id_int = None
    else:
        selected_clinic_id_int = None
    
    for t in tariff_qs:
        key = f"{t.service_type_id}_{t.insurance_type_id}"
        existing_tariffs[key] = t.fee
    
    if request.method == 'POST':
        clinic_id = request.POST.get('clinic_id') or None
        is_general = request.POST.get('is_general') == 'on'
        
        if is_general:
            clinic_id = None
        
        tariffs_data = []
        for service in services:
            for insurance in insurances:
                field_name = f"fee_{service.id}_{insurance.id}"
                fee_val = request.POST.get(field_name, '').replace(',', '')
                
                if fee_val and int(fee_val) > 0:
                    tariffs_data.append({
                        'service_type_id': service.id,
                        'insurance_type_id': insurance.id,
                        'fee': int(fee_val),
                        'clinic_id': clinic_id,
                    })
        
        if tariffs_data:
            created_tariffs, created_count, updated_count = TariffService.bulk_create_tariffs(doctor.id, tariffs_data)
            messages.success(
                request,
                f'{created_count} تعرفه جدید ایجاد و {updated_count} تعرفه بروزرسانی شد'
            )
            return redirect('doctor_tariffs')
        else:
            messages.warning(request, 'هیچ تعرفه‌ای وارد نشده است')
    
    context = {
        'doctor': doctor,
        'doctor_clinics': doctor_clinics,
        'services': services,
        'insurances': insurances,
        'existing_tariffs': existing_tariffs,
        'selected_clinic': selected_clinic_id,
    }
    return render(request, 'doctors/bulk_tariffs.html', context)


# ===== API تعرفه‌ها =====

@login_required
def api_calculate_tariff(request, doctor_id):
    """محاسبه تعرفه برای فرآیند رزرو نوبت (AJAX)"""
    service_type_id = request.GET.get('service_type')
    insurance_type_id = request.GET.get('insurance_type')
    clinic_id = request.GET.get('clinic')
    
    if not service_type_id or not insurance_type_id:
        return JsonResponse({
            'success': False,
            'message': 'نوع خدمت و بیمه الزامی است'
        })
    
    result = TariffService.calculate_booking_fee(
        doctor_id=doctor_id,
        service_type_id=int(service_type_id),
        insurance_type_id=int(insurance_type_id),
        clinic_id=int(clinic_id) if clinic_id else None
    )
    
    return JsonResponse(result)


@login_required
def api_doctor_services(request, doctor_id):
    """دریافت خدمات فعال یک پزشک (AJAX)"""
    clinic_id = request.GET.get('clinic')
    
    services = TariffService.get_doctor_services(
        doctor_id=doctor_id,
        clinic_id=int(clinic_id) if clinic_id else None
    )
    
    data = [
        {'id': s.id, 'name': s.name, 'icon': s.icon}
        for s in services
    ]
    
    return JsonResponse({'success': True, 'services': data})


@login_required
def api_doctor_insurances(request, doctor_id, service_id):
    """دریافت بیمه‌های فعال برای یک خدمت (AJAX)"""
    clinic_id = request.GET.get('clinic')
    
    insurances = TariffService.get_doctor_insurances(
        doctor_id=doctor_id,
        service_type_id=service_id,
        clinic_id=int(clinic_id) if clinic_id else None
    )
    
    data = [
        {'id': i.id, 'name': i.name, 'icon': i.icon}
        for i in insurances
    ]
    
    return JsonResponse({'success': True, 'insurances': data})


# ===== API ها =====

@login_required
def api_search_patient(request):
    """جستجوی بیمار بر اساس شماره موبایل (AJAX)"""
    phone = request.GET.get('phone', '').strip()
    
    if not phone or len(phone) != 11:
        return JsonResponse({'found': False, 'message': 'شماره موبایل نامعتبر است'})
    
    try:
        patient = User.objects.get(phone=phone)
        return JsonResponse({
            'found': True,
            'id': patient.id,
            'name': patient.get_full_name(),
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'national_code': patient.national_code or '',
            'gender': patient.gender or '',
        })
    except User.DoesNotExist:
        return JsonResponse({'found': False, 'message': 'بیماری با این شماره یافت نشد'})


@login_required
@require_POST
def api_confirm_appointment(request, appointment_id):
    """تأیید نوبت"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        appointment.status = 'confirmed'
        appointment.save()
        
        return JsonResponse({'success': True, 'message': 'نوبت تأیید شد'})
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'نوبت یافت نشد'})


@login_required
@require_POST
def api_cancel_appointment(request, appointment_id):
    """لغو نوبت"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        appointment.status = 'cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.save()
        
        return JsonResponse({'success': True, 'message': 'نوبت لغو شد'})
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'نوبت یافت نشد'})


@login_required
@require_POST
def api_mark_arrived(request, appointment_id):
    """ثبت حضور بیمار"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        appointment.status = 'arrived'
        appointment.arrived_at = timezone.now()
        appointment.save()
        
        return JsonResponse({'success': True, 'message': 'حضور ثبت شد'})
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'نوبت یافت نشد'})


@login_required
@require_POST
def api_start_visit(request, appointment_id):
    """شروع ویزیت"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        # پایان ویزیت قبلی
        Appointment.objects.filter(
            doctor=doctor,
            date=timezone.now().date(),
            status='in_progress'
        ).update(status='visited', visited_at=timezone.now())
        
        appointment.status = 'in_progress'
        appointment.save()
        
        return JsonResponse({'success': True, 'message': 'ویزیت شروع شد'})
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'نوبت یافت نشد'})


@login_required
@require_POST
def api_end_visit(request, appointment_id):
    """پایان ویزیت"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        appointment.status = 'visited'
        appointment.visited_at = timezone.now()
        appointment.save()
        
        return JsonResponse({'success': True, 'message': 'ویزیت پایان یافت'})
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'نوبت یافت نشد'})


@login_required
def api_medical_terms(request):
    """
    API اتوکامپلیت اصطلاحات پزشکی
    GET /api/v1/medical-terms/?category=symptom&q=سر
    جستجو در نام فارسی و انگلیسی، مرتب بر اساس محبوبیت
    """
    category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    
    valid_categories = ('symptom', 'diagnosis', 'medication', 'lab_test', 'imaging', 'procedure')
    if not category or category not in valid_categories:
        return JsonResponse({'success': False, 'message': 'دسته‌بندی نامعتبر'})
    
    terms = MedicalTerm.objects.filter(category=category)
    
    if query:
        terms = terms.filter(
            Q(name_fa__icontains=query) | Q(name_en__icontains=query)
        )
    
    # مرتب‌سازی: اول محبوب‌ترین، بعد الفبایی
    terms = terms.order_by('-usage_count', 'name_fa')[:20]
    
    results = [
        {
            'id': t.id,
            'name_fa': t.name_fa,
            'name_en': t.name_en or '',
            'is_default': t.is_default,
        }
        for t in terms
    ]
    
    return JsonResponse({'success': True, 'results': results})


@login_required
@require_POST
def api_add_medical_term(request):
    """
    API افزودن اصطلاح جدید توسط پزشک
    POST /api/v1/medical-terms/add/
    {category, name_fa, name_en}
    """
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'دسترسی ندارید'})
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST
    
    category = data.get('category', '')
    name_fa = data.get('name_fa', '').strip()
    name_en = data.get('name_en', '').strip()
    
    valid_categories = ('symptom', 'diagnosis', 'medication', 'lab_test', 'imaging', 'procedure')
    if not category or category not in valid_categories:
        return JsonResponse({'success': False, 'message': 'دسته‌بندی نامعتبر'})
    
    if not name_fa:
        return JsonResponse({'success': False, 'message': 'نام فارسی الزامی است'})
    
    if len(name_fa) < 2:
        return JsonResponse({'success': False, 'message': 'نام باید حداقل ۲ حرف باشد'})
    
    # بررسی تکراری نبودن
    if MedicalTerm.objects.filter(category=category, name_fa=name_fa).exists():
        existing = MedicalTerm.objects.get(category=category, name_fa=name_fa)
        return JsonResponse({
            'success': True,
            'message': 'این مورد قبلاً وجود دارد',
            'term': {
                'id': existing.id,
                'name_fa': existing.name_fa,
                'name_en': existing.name_en or '',
            }
        })
    
    term = MedicalTerm.objects.create(
        category=category,
        name_fa=name_fa,
        name_en=name_en or None,
        is_default=False,
        added_by=request.user,
    )
    
    return JsonResponse({
        'success': True,
        'message': 'با موفقیت اضافه شد',
        'term': {
            'id': term.id,
            'name_fa': term.name_fa,
            'name_en': term.name_en or '',
        }
    })


# =============================================================================
# مدیریت منشی توسط پزشک
# =============================================================================

@login_required
def doctor_secretaries(request):
    """لیست منشی‌های پزشک"""
    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = get_object_or_404(Doctor, user=request.user)

    # فعلاً منشی‌ها را از جدول User با نقش secretary لیست می‌کنیم
    # در آینده می‌شه مدل ارتباطی DoctorSecretary اضافه کرد
    secretaries = User.objects.filter(role='secretary', is_active=True)

    context = {
        'doctor': doctor,
        'secretaries': secretaries,
    }
    return render(request, 'doctors/secretaries.html', context)


@login_required
def doctor_add_secretary(request):
    """افزودن منشی جدید توسط پزشک"""
    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')

        # اعتبارسنجی
        if not phone or len(phone) != 11 or not phone.startswith('09'):
            messages.error(request, 'شماره موبایل معتبر نیست')
        elif not first_name or not last_name:
            messages.error(request, 'نام و نام خانوادگی الزامی است')
        elif not password or len(password) < 6:
            messages.error(request, 'رمز عبور باید حداقل ۶ کاراکتر باشد')
        elif User.objects.filter(phone=phone).exists():
            messages.error(request, 'این شماره موبایل قبلاً ثبت شده')
        else:
            try:
                user = User.objects.create_user(
                    phone=phone,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='secretary',
                )
                messages.success(request, f'منشی «{user.get_full_name()}» با موفقیت ایجاد شد')
                return redirect('doctor_secretaries')
            except Exception as e:
                messages.error(request, f'خطا: {str(e)}')

    context = {
        'doctor': doctor,
    }
    return render(request, 'doctors/add_secretary.html', context)

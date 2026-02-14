"""
Views برای بخش بیماران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان

سیستم رزرو نوبت واقعی بر اساس:
- تقویم کاری پزشک (WorkSchedule)
- تعطیلات پزشک (DoctorHoliday)
- مراکز پزشکی (DoctorClinic)
- نوبت‌های رزرو شده (Appointment)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time as dt_time
from apps.doctors.models import Doctor, DoctorClinic, WorkSchedule, DoctorHoliday
from apps.clinics.models import Clinic
from apps.appointments.models import Appointment
from .models import MedicalRecord, MedicalFile


# ============================================================
#  سرویس محاسبه تایم‌های واقعی
# ============================================================

def get_jalali_day_of_week(date):
    """
    تبدیل روز هفته میلادی به شمسی
    شنبه=0, یکشنبه=1, ..., جمعه=6
    """
    # Python: Monday=0 ... Sunday=6
    # ما نیاز داریم: Saturday=0 ... Friday=6
    mapping = {
        5: 0,  # Saturday → شنبه
        6: 1,  # Sunday → یکشنبه
        0: 2,  # Monday → دوشنبه
        1: 3,  # Tuesday → سه‌شنبه
        2: 4,  # Wednesday → چهارشنبه
        3: 5,  # Thursday → پنج‌شنبه
        4: 6,  # Friday → جمعه
    }
    return mapping[date.weekday()]


def get_doctor_working_dates(doctor, clinic, max_days=None):
    """
    دریافت تاریخ‌های کاری واقعی پزشک در یک مرکز

    بر اساس:
    - تقویم کاری پزشک (WorkSchedule) برای مرکز مشخص
    - تعطیلات پزشک (DoctorHoliday)
    - حداکثر روزهای رزرو آینده (max_advance_days)
    - حداکثر نوبت روزانه

    Returns:
        list of dict: [{'date': date, 'day_of_week': int, 'day_name': str, 'schedules': [...]}]
    """
    if max_days is None:
        max_days = doctor.max_advance_days or 30

    today = timezone.now().date()

    # ۱. دریافت روزهای کاری پزشک در این مرکز
    work_schedules = WorkSchedule.objects.filter(
        doctor=doctor,
        clinic=clinic,
        is_active=True
    ).order_by('day_of_week', 'start_time')

    if not work_schedules.exists():
        return []

    # ساخت دیکشنری روزهای کاری: {day_of_week: [schedule1, schedule2, ...]}
    schedule_map = {}
    for ws in work_schedules:
        if ws.day_of_week not in schedule_map:
            schedule_map[ws.day_of_week] = []
        schedule_map[ws.day_of_week].append(ws)

    # ۲. دریافت تعطیلات پزشک
    holidays = set(
        DoctorHoliday.objects.filter(
            doctor=doctor,
            date__gte=today,
            date__lte=today + timedelta(days=max_days)
        ).filter(
            Q(clinic=clinic) | Q(clinic__isnull=True)
        ).values_list('date', flat=True)
    )

    # ۳. تولید لیست تاریخ‌های کاری واقعی
    working_dates = []
    day_names = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']

    for i in range(max_days):
        date = today + timedelta(days=i)
        jalali_dow = get_jalali_day_of_week(date)

        # آیا این روز در تقویم کاری هست؟
        if jalali_dow not in schedule_map:
            continue

        # آیا تعطیل هست؟
        if date in holidays:
            continue

        # بررسی آیا هنوز ظرفیت دارد
        booked_count = Appointment.objects.filter(
            doctor=doctor,
            clinic=clinic,
            date=date,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress']
        ).count()

        # حداکثر نوبت از WorkSchedule یا از تنظیمات پزشک
        schedules_for_day = schedule_map[jalali_dow]
        max_for_day = schedules_for_day[0].max_appointments or doctor.max_daily_appointments

        if booked_count >= max_for_day:
            continue

        working_dates.append({
            'date': date,
            'date_str': date.isoformat(),
            'day_of_week': jalali_dow,
            'day_name': day_names[jalali_dow],
            'is_today': (date == today),
            'schedules': schedules_for_day,
            'booked_count': booked_count,
            'max_appointments': max_for_day,
            'remaining': max_for_day - booked_count,
        })

    return working_dates


def get_available_time_slots(doctor, clinic, date):
    """
    دریافت تایم‌های خالی واقعی برای یک تاریخ مشخص

    بر اساس:
    - ساعات کاری پزشک در آن روز هفته و مرکز
    - مدت ویزیت و فاصله بین نوبت‌ها
    - نوبت‌های رزرو شده موجود
    - اگر امروز باشد، ساعت‌های گذشته حذف شوند

    Returns:
        list of dict: [{'time': '08:00', 'time_obj': time, 'is_available': True/False}]
    """
    jalali_dow = get_jalali_day_of_week(date)

    # ۱. دریافت ساعات کاری
    work_schedules = WorkSchedule.objects.filter(
        doctor=doctor,
        clinic=clinic,
        day_of_week=jalali_dow,
        is_active=True
    ).order_by('start_time')

    if not work_schedules.exists():
        return []

    # ۲. مدت هر تایم (ویزیت + فاصله)
    # اگر مرکز تنظیمات سفارشی داره استفاده کن
    doctor_clinic = DoctorClinic.objects.filter(
        doctor=doctor, clinic=clinic
    ).first()

    visit_duration = (
        doctor_clinic.custom_visit_duration if doctor_clinic and doctor_clinic.custom_visit_duration
        else doctor.visit_duration
    )
    gap = doctor.gap_between_visits
    slot_duration = visit_duration + gap  # مجموع زمان هر اسلات

    # ۳. نوبت‌های رزرو شده
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            clinic=clinic,
            date=date,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress']
        ).values_list('time', flat=True)
    )

    # ۴. ساعت فعلی (اگر امروز باشد)
    now = timezone.now()
    is_today = (date == now.date())
    current_time = now.time() if is_today else None

    # ۵. تولید تایم‌ها
    time_slots = []

    for ws in work_schedules:
        current_slot = datetime.combine(date, ws.start_time)
        end_datetime = datetime.combine(date, ws.end_time)

        while current_slot + timedelta(minutes=visit_duration) <= end_datetime:
            slot_time = current_slot.time()
            time_str = slot_time.strftime('%H:%M')

            # بررسی موجود بودن
            is_booked = slot_time in booked_times
            is_past = is_today and current_time and slot_time <= current_time

            time_slots.append({
                'time': time_str,
                'time_obj': slot_time,
                'is_available': not is_booked and not is_past,
                'is_booked': is_booked,
                'is_past': is_past,
            })

            current_slot += timedelta(minutes=slot_duration)

    return time_slots


# ============================================================
#  داشبورد بیمار
# ============================================================

@login_required
def patient_dashboard(request):
    """داشبورد بیمار"""
    user = request.user
    today = timezone.now().date()

    # نوبت‌های آینده
    appointments = Appointment.objects.filter(
        patient=user,
        date__gte=today,
        status__in=['pending', 'confirmed']
    ).select_related('doctor', 'doctor__user', 'clinic').order_by('date', 'time')[:5]

    upcoming_count = appointments.count()
    completed_count = Appointment.objects.filter(patient=user, status='visited').count()
    records_count = MedicalRecord.objects.filter(patient=user).count()
    my_doctors_count = Appointment.objects.filter(patient=user).values('doctor').distinct().count()

    active_appointment = Appointment.objects.filter(
        patient=user, date__gte=today, status='confirmed'
    ).select_related('doctor', 'doctor__user').order_by('date', 'time').first()

    recent_visits = Appointment.objects.filter(
        patient=user, status='visited'
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


# ============================================================
#  رزرو نوبت - مرحله ۱: انتخاب پزشک
# ============================================================

@login_required
def book_appointment(request):
    """صفحه رزرو نوبت - انتخاب پزشک"""
    doctors = Doctor.objects.filter(
        is_active=True,
        allows_online_booking=True
    ).select_related('user')

    # فیلتر تخصص
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization=specialization)

    # جستجو
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(specialization__icontains=search)
        )

    specializations = Doctor.objects.filter(
        is_active=True
    ).values_list('specialization', flat=True).distinct()

    context = {
        'doctors': doctors,
        'specializations': specializations,
        'selected_specialization': specialization,
        'search_query': search,
    }
    return render(request, 'patients/book_appointment.html', context)


# ============================================================
#  رزرو نوبت - مرحله ۲: انتخاب مرکز، تاریخ و ساعت
# ============================================================

@login_required
def book_appointment_doctor(request, doctor_id):
    """صفحه رزرو نوبت - انتخاب مرکز، تاریخ و ساعت"""
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)

    # دریافت مراکز فعال پزشک
    doctor_clinics = DoctorClinic.objects.filter(
        doctor=doctor,
        is_active=True
    ).select_related('clinic').order_by('-is_primary')

    clinics = [dc.clinic for dc in doctor_clinics if dc.clinic.is_active]

    # مرکز انتخاب‌شده (از URL یا اولین مرکز)
    selected_clinic_id = request.GET.get('clinic')
    selected_clinic = None

    if selected_clinic_id:
        try:
            selected_clinic = Clinic.objects.get(
                id=int(selected_clinic_id),
                is_active=True
            )
            # بررسی اینکه پزشک واقعاً در این مرکز کار میکنه
            if not doctor_clinics.filter(clinic=selected_clinic).exists():
                selected_clinic = None
        except (ValueError, Clinic.DoesNotExist):
            selected_clinic = None

    # اگر هیچ مرکزی انتخاب نشده، اولین مرکز
    if not selected_clinic and clinics:
        selected_clinic = clinics[0]

    # دریافت تاریخ‌های کاری واقعی
    working_dates = []
    if selected_clinic:
        working_dates = get_doctor_working_dates(doctor, selected_clinic)

    # پست فرم رزرو
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        clinic_id = request.POST.get('clinic_id')

        if not date_str or not time_str or not clinic_id:
            messages.error(request, 'لطفاً مرکز، تاریخ و ساعت را انتخاب کنید')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            booking_time = datetime.strptime(time_str, '%H:%M').time()
            booking_clinic = Clinic.objects.get(id=int(clinic_id), is_active=True)
        except (ValueError, Clinic.DoesNotExist):
            messages.error(request, 'اطلاعات نامعتبر')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی اعتبار مرکز
        if not doctor_clinics.filter(clinic=booking_clinic).exists():
            messages.error(request, 'پزشک در این مرکز فعالیت ندارد')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی تاریخ گذشته
        if booking_date < timezone.now().date():
            messages.error(request, 'امکان رزرو برای تاریخ گذشته وجود ندارد')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی تعطیلی
        is_holiday = DoctorHoliday.objects.filter(
            doctor=doctor,
            date=booking_date
        ).filter(
            Q(clinic=booking_clinic) | Q(clinic__isnull=True)
        ).exists()
        if is_holiday:
            messages.error(request, 'پزشک در این تاریخ تعطیل است')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی برنامه کاری
        jalali_dow = get_jalali_day_of_week(booking_date)
        has_schedule = WorkSchedule.objects.filter(
            doctor=doctor,
            clinic=booking_clinic,
            day_of_week=jalali_dow,
            is_active=True
        ).exists()
        if not has_schedule:
            messages.error(request, 'پزشک در این روز در این مرکز برنامه‌ای ندارد')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی نوبت تکراری
        if Appointment.objects.filter(
            doctor=doctor,
            clinic=booking_clinic,
            date=booking_date,
            time=booking_time,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress']
        ).exists():
            messages.error(request, 'این زمان قبلاً رزرو شده است. لطفاً زمان دیگری انتخاب کنید.')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی ظرفیت روزانه
        booked_count = Appointment.objects.filter(
            doctor=doctor,
            clinic=booking_clinic,
            date=booking_date,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress']
        ).count()
        if booked_count >= doctor.max_daily_appointments:
            messages.error(request, 'ظرفیت نوبت این روز تکمیل شده است')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # بررسی نوبت تکراری بیمار در همان روز و پزشک
        if Appointment.objects.filter(
            patient=request.user,
            doctor=doctor,
            date=booking_date,
            status__in=['pending', 'confirmed']
        ).exists():
            messages.error(request, 'شما قبلاً در این تاریخ نزد این پزشک نوبت دارید')
            return redirect('patient_book_doctor', doctor_id=doctor_id)

        # محاسبه شماره صف
        queue_number = booked_count + 1

        # دریافت هزینه ویزیت
        doctor_clinic_obj = doctor_clinics.filter(clinic=booking_clinic).first()
        visit_fee = doctor_clinic_obj.get_visit_fee() if doctor_clinic_obj else (doctor.visit_fee or 0)

        # ایجاد نوبت
        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            clinic=booking_clinic,
            date=booking_date,
            time=booking_time,
            status='pending',
            payment_status='unpaid',
            payment_amount=visit_fee,
            queue_number=queue_number,
            booking_source='online',
        )

        messages.success(
            request,
            f'نوبت شما با موفقیت ثبت شد. شماره نوبت: {queue_number} | '
            f'مرکز: {booking_clinic.name}'
        )
        return redirect('patient_appointments')

    # DoctorClinic اطلاعات اضافی هر مرکز
    clinics_info = []
    for dc in doctor_clinics:
        if not dc.clinic.is_active:
            continue
        clinics_info.append({
            'clinic': dc.clinic,
            'is_primary': dc.is_primary,
            'visit_fee': dc.get_visit_fee(),
            'visit_duration': dc.get_visit_duration(),
            'room_number': dc.room_number,
        })

    context = {
        'doctor': doctor,
        'clinics': clinics,
        'clinics_info': clinics_info,
        'selected_clinic': selected_clinic,
        'working_dates': working_dates,
    }
    return render(request, 'patients/book_doctor.html', context)


# ============================================================
#  API - دریافت تاریخ‌های کاری (AJAX)
# ============================================================

@login_required
def api_doctor_dates(request, doctor_id):
    """
    API: دریافت تاریخ‌های کاری واقعی پزشک در یک مرکز
    GET /patient/book/<doctor_id>/dates/?clinic=<clinic_id>
    """
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    clinic_id = request.GET.get('clinic')

    if not clinic_id:
        return JsonResponse({'success': False, 'message': 'مرکز مشخص نشده'})

    try:
        clinic = Clinic.objects.get(id=int(clinic_id), is_active=True)
    except (ValueError, Clinic.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'مرکز نامعتبر'})

    # بررسی ارتباط پزشک-مرکز
    if not DoctorClinic.objects.filter(doctor=doctor, clinic=clinic, is_active=True).exists():
        return JsonResponse({'success': False, 'message': 'پزشک در این مرکز فعالیت ندارد'})

    working_dates = get_doctor_working_dates(doctor, clinic)

    dates_data = []
    for wd in working_dates:
        dates_data.append({
            'date': wd['date_str'],
            'day_name': wd['day_name'],
            'is_today': wd['is_today'],
            'remaining': wd['remaining'],
            'max_appointments': wd['max_appointments'],
        })

    return JsonResponse({
        'success': True,
        'dates': dates_data,
        'clinic_name': clinic.name,
    })


# ============================================================
#  API - دریافت تایم‌های خالی (AJAX)
# ============================================================

@login_required
def api_doctor_times(request, doctor_id):
    """
    API: دریافت ساعت‌های خالی واقعی پزشک
    GET /patient/book/<doctor_id>/times/?clinic=<clinic_id>&date=<YYYY-MM-DD>
    """
    doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
    clinic_id = request.GET.get('clinic')
    date_str = request.GET.get('date')

    if not clinic_id or not date_str:
        return JsonResponse({'success': False, 'message': 'پارامترهای ناقص'})

    try:
        clinic = Clinic.objects.get(id=int(clinic_id), is_active=True)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, Clinic.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'پارامترهای نامعتبر'})

    # بررسی ارتباط پزشک-مرکز
    if not DoctorClinic.objects.filter(doctor=doctor, clinic=clinic, is_active=True).exists():
        return JsonResponse({'success': False, 'message': 'پزشک در این مرکز فعالیت ندارد'})

    # بررسی تعطیلی
    is_holiday = DoctorHoliday.objects.filter(
        doctor=doctor, date=date
    ).filter(Q(clinic=clinic) | Q(clinic__isnull=True)).exists()

    if is_holiday:
        return JsonResponse({'success': False, 'message': 'پزشک در این تاریخ تعطیل است'})

    time_slots = get_available_time_slots(doctor, clinic, date)

    # هزینه ویزیت
    dc = DoctorClinic.objects.filter(doctor=doctor, clinic=clinic).first()
    visit_fee = dc.get_visit_fee() if dc else (doctor.visit_fee or 0)
    visit_duration = dc.get_visit_duration() if dc else doctor.visit_duration

    slots_data = []
    for slot in time_slots:
        slots_data.append({
            'time': slot['time'],
            'is_available': slot['is_available'],
            'is_booked': slot['is_booked'],
            'is_past': slot.get('is_past', False),
        })

    available_count = sum(1 for s in slots_data if s['is_available'])

    return JsonResponse({
        'success': True,
        'slots': slots_data,
        'total_slots': len(slots_data),
        'available_count': available_count,
        'visit_fee': int(visit_fee),
        'visit_duration': visit_duration,
    })


# ============================================================
#  نوبت‌های من
# ============================================================

@login_required
def my_appointments(request):
    """نوبت‌های من"""
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('doctor__user', 'clinic').order_by('-date', '-time')

    status = request.GET.get('status')
    if status:
        appointments = appointments.filter(status=status)

    context = {
        'appointments': appointments,
        'selected_status': status,
    }
    return render(request, 'patients/appointments.html', context)


# ============================================================
#  لغو نوبت
# ============================================================

@login_required
def cancel_appointment(request, pk):
    """لغو نوبت"""
    appointment = get_object_or_404(Appointment, pk=pk, patient=request.user)

    if appointment.status in ['cancelled', 'visited']:
        messages.error(request, 'امکان لغو این نوبت وجود ندارد')
        return redirect('patient_appointments')

    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.cancel_reason = request.POST.get('reason', '')
        appointment.cancelled_by = request.user
        appointment.save()

        messages.success(request, 'نوبت با موفقیت لغو شد')
        return redirect('patient_appointments')

    return render(request, 'patients/cancel_appointment.html', {'appointment': appointment})


# ============================================================
#  صف زنده
# ============================================================

@login_required
def live_queue(request):
    """
    صف زنده - نمایش وضعیت نوبت فعال بیمار

    اولویت:
    1. نوبت امروز
    2. نزدیک‌ترین نوبت آینده
    """
    today = timezone.now().date()
    now = timezone.now()

    # ۱. اول نوبت امروز رو چک کن
    active_appointment = Appointment.objects.filter(
        patient=request.user,
        date=today,
        status__in=['pending', 'confirmed', 'arrived', 'in_progress']
    ).select_related('doctor__user', 'clinic').order_by('time').first()

    # ۲. اگه امروز نداره، نزدیک‌ترین نوبت آینده
    if not active_appointment:
        active_appointment = Appointment.objects.filter(
            patient=request.user,
            date__gt=today,
            status__in=['pending', 'confirmed']
        ).select_related('doctor__user', 'clinic').order_by('date', 'time').first()

    queue_info = None
    upcoming_appointments = []

    if active_appointment:
        # محاسبه تعداد نفرات جلوتر
        ahead_count = Appointment.objects.filter(
            doctor=active_appointment.doctor,
            clinic=active_appointment.clinic,
            date=active_appointment.date,
            time__lt=active_appointment.time,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress']
        ).count()

        # محاسبه تعداد کل نوبت‌های آن روز
        total_day = Appointment.objects.filter(
            doctor=active_appointment.doctor,
            clinic=active_appointment.clinic,
            date=active_appointment.date,
            status__in=['pending', 'confirmed', 'arrived', 'in_progress', 'visited']
        ).count()

        # تعداد ویزیت‌شده‌ها
        visited_count = Appointment.objects.filter(
            doctor=active_appointment.doctor,
            clinic=active_appointment.clinic,
            date=active_appointment.date,
            status='visited'
        ).count()

        # محاسبه زمان تقریبی
        estimated_wait = ahead_count * (
            active_appointment.doctor.visit_duration +
            active_appointment.doctor.gap_between_visits
        )

        is_today = (active_appointment.date == today)
        is_future = (active_appointment.date > today)

        queue_info = {
            'appointment': active_appointment,
            'queue_number': active_appointment.queue_number or (ahead_count + 1),
            'ahead_count': ahead_count,
            'estimated_time': active_appointment.estimated_time,
            'estimated_wait_minutes': estimated_wait,
            'total_day': total_day,
            'visited_count': visited_count,
            'is_today': is_today,
            'is_future': is_future,
        }

    # سایر نوبت‌های آینده (بعد از نوبت فعال)
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        date__gte=today,
        status__in=['pending', 'confirmed']
    ).select_related('doctor__user', 'clinic').order_by('date', 'time')

    if active_appointment:
        upcoming_appointments = upcoming_appointments.exclude(id=active_appointment.id)

    upcoming_appointments = upcoming_appointments[:5]

    context = {
        'active_appointment': active_appointment,
        'queue_info': queue_info,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'patients/queue.html', context)


# ============================================================
#  پرونده پزشکی
# ============================================================

@login_required
def medical_records(request):
    """سوابق پزشکی"""
    records = MedicalRecord.objects.filter(
        patient=request.user
    ).select_related('doctor__user', 'appointment').order_by('-created_at')

    context = {'records': records}
    return render(request, 'patients/records.html', context)


@login_required
def record_detail(request, pk):
    """جزئیات پرونده پزشکی"""
    record = get_object_or_404(MedicalRecord, pk=pk, patient=request.user)
    files = record.files.all()

    context = {'record': record, 'files': files}
    return render(request, 'patients/record_detail.html', context)


@login_required
def prescriptions(request):
    """نسخه‌ها"""
    records = MedicalRecord.objects.filter(
        patient=request.user,
        prescription__isnull=False
    ).exclude(prescription='').select_related('doctor__user').order_by('-created_at')

    context = {'records': records}
    return render(request, 'patients/prescriptions.html', context)


@login_required
def medical_files(request):
    """فایل‌های پزشکی"""
    files = MedicalFile.objects.filter(
        record__patient=request.user
    ).select_related('record__doctor__user').order_by('-created_at')

    context = {'files': files}
    return render(request, 'patients/files.html', context)


@login_required
def upload_file(request):
    """آپلود فایل پزشکی"""
    if request.method == 'POST':
        messages.success(request, 'فایل با موفقیت آپلود شد')
        return redirect('patient_files')

    return render(request, 'patients/upload_file.html')


@login_required
def payments(request):
    """پرداخت‌ها"""
    from apps.payments.models import Transaction

    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('appointment__doctor__user').order_by('-created_at')

    context = {'transactions': transactions}
    return render(request, 'patients/payments.html', context)

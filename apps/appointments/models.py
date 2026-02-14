"""
مدل‌های اپلیکیشن نوبت‌دهی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Appointment(models.Model):
    """
    مدل نوبت
    """
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('arrived', 'حاضر شده'),
        ('in_progress', 'در حال ویزیت'),
        ('visited', 'ویزیت شده'),
        ('cancelled', 'لغو شده'),
        ('no_show', 'عدم حضور'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'پرداخت نشده'),
        ('deposit', 'بیعانه پرداخت شده'),
        ('paid', 'پرداخت کامل'),
        ('refunded', 'بازپرداخت شده'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('onsite', 'پرداخت در مطب'),
        ('online_full', 'پرداخت آنلاین کامل'),
        ('online_deposit', 'پرداخت بیعانه آنلاین'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('online', 'رزرو آنلاین'),
        ('phone', 'رزرو تلفنی'),
        ('onsite', 'حضوری'),
        ('secretary', 'توسط منشی'),
    ]
    
    # روابط اصلی
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='بیمار'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='مرکز',
        null=True,
        blank=True
    )
    
    # ارتباط با سیستم تعرفه (فاز 4)
    service_type = models.ForeignKey(
        'doctors.ServiceType',
        on_delete=models.SET_NULL,
        related_name='appointments',
        verbose_name='نوع خدمت',
        null=True,
        blank=True
    )
    insurance_type = models.ForeignKey(
        'doctors.InsuranceType',
        on_delete=models.SET_NULL,
        related_name='appointments',
        verbose_name='نوع بیمه',
        null=True,
        blank=True
    )
    tariff = models.ForeignKey(
        'doctors.DoctorTariff',
        on_delete=models.SET_NULL,
        related_name='appointments',
        verbose_name='تعرفه اعمال‌شده',
        null=True,
        blank=True
    )
    tariff_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ تعرفه در زمان رزرو (ریال)',
        help_text='Snapshot مبلغ تعرفه در لحظه رزرو - تغییرات بعدی تعرفه تأثیری روی نوبت ندارد'
    )
    
    # زمان نوبت
    date = models.DateField(
        verbose_name='تاریخ نوبت'
    )
    time = models.TimeField(
        verbose_name='ساعت نوبت'
    )
    
    # صف
    queue_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='شماره صف'
    )
    estimated_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='زمان تقریبی ویزیت'
    )
    
    # وضعیت‌ها
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    booking_source = models.CharField(
        max_length=20,
        choices=BOOKING_SOURCE_CHOICES,
        default='online',
        verbose_name='منبع رزرو'
    )
    
    # پرداخت
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid',
        verbose_name='وضعیت پرداخت'
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='نوع پرداخت'
    )
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='هزینه ویزیت'
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ بیعانه'
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ پرداخت شده'
    )
    
    # یادداشت‌ها
    patient_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت بیمار'
    )
    secretary_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت منشی'
    )
    doctor_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت پزشک'
    )
    
    # ایجادکننده (برای نوبت‌های غیر آنلاین)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_appointments',
        verbose_name='ایجاد شده توسط'
    )
    
    # تاریخ‌های مهم
    arrived_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='زمان حضور'
    )
    visit_started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='زمان شروع ویزیت'
    )
    visited_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='زمان پایان ویزیت'
    )
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='زمان لغو'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments',
        verbose_name='لغو شده توسط'
    )
    cancel_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='دلیل لغو'
    )
    
    # اعلان‌ها
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='یادآوری ارسال شده'
    )
    confirm_sms_sent = models.BooleanField(
        default=False,
        verbose_name='پیامک تأیید ارسال شده'
    )
    
    # تاریخ‌های سیستم
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        db_table = 'appointments_appointment'
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
        ordering = ['-date', 'time']
        indexes = [
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['patient', 'date']),
            models.Index(fields=['clinic', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['date', 'queue_number']),
            models.Index(fields=['service_type']),
            models.Index(fields=['insurance_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date', 'time'],
                condition=~models.Q(status='cancelled'),
                name='unique_appointment_slot'
            )
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_title()} - {self.date}"
    
    def get_datetime(self):
        """برگرداندن تاریخ و ساعت به صورت datetime"""
        from datetime import datetime
        return datetime.combine(self.date, self.time)
    
    def is_today(self):
        """آیا نوبت امروز است؟"""
        return self.date == timezone.now().date()
    
    def is_past(self):
        """آیا نوبت گذشته؟"""
        return self.get_datetime() < timezone.now()
    
    def is_cancellable(self):
        """آیا نوبت قابل لغو است؟"""
        if self.status in ['cancelled', 'visited', 'no_show']:
            return False
        
        cancel_deadline = timezone.now() + timedelta(hours=self.doctor.min_cancel_hours)
        return self.get_datetime() > cancel_deadline
    
    def get_remaining_amount(self):
        """محاسبه مبلغ باقیمانده"""
        return self.payment_amount - self.paid_amount
    
    def calculate_queue_position(self):
        """محاسبه جایگاه در صف"""
        ahead_count = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            time__lt=self.time,
            status__in=['confirmed', 'arrived', 'in_progress']
        ).count()
        return ahead_count
    
    def get_status_badge_class(self):
        """کلاس CSS برای نمایش وضعیت"""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'arrived': 'primary',
            'in_progress': 'primary',
            'visited': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary',
        }
        return status_classes.get(self.status, 'secondary')


class AppointmentHistory(models.Model):
    """
    مدل تاریخچه تغییرات نوبت
    """
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='نوبت'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='تغییر توسط'
    )
    field_name = models.CharField(
        max_length=50,
        verbose_name='فیلد تغییر یافته'
    )
    old_value = models.TextField(
        blank=True,
        null=True,
        verbose_name='مقدار قبلی'
    )
    new_value = models.TextField(
        blank=True,
        null=True,
        verbose_name='مقدار جدید'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ'
    )
    
    class Meta:
        db_table = 'appointments_appointment_history'
        verbose_name = 'تاریخچه نوبت'
        verbose_name_plural = 'تاریخچه نوبت‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment} - {self.field_name}"


class TimeSlot(models.Model):
    """
    مدل تایم‌های قابل رزرو (برای نمایش و مدیریت)
    """
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='مرکز'
    )
    date = models.DateField(
        verbose_name='تاریخ'
    )
    time = models.TimeField(
        verbose_name='ساعت'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='موجود'
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='مسدود شده'
    )
    block_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='دلیل مسدودیت'
    )
    
    class Meta:
        db_table = 'appointments_time_slot'
        verbose_name = 'تایم'
        verbose_name_plural = 'تایم‌ها'
        ordering = ['date', 'time']
        unique_together = ['doctor', 'clinic', 'date', 'time']
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.time}"

"""
مدل‌های اپلیکیشن صف زنده - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings


class QueueStatus(models.Model):
    """
    مدل وضعیت صف (برای ذخیره وضعیت فعلی)
    """
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='queue_statuses',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='queue_statuses',
        verbose_name='مرکز'
    )
    date = models.DateField(
        verbose_name='تاریخ'
    )
    
    # وضعیت فعلی
    current_queue_number = models.PositiveIntegerField(
        default=0,
        verbose_name='شماره صف فعلی'
    )
    current_appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_queue_status',
        verbose_name='نوبت فعلی'
    )
    
    # آمار
    total_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='کل نوبت‌ها'
    )
    completed_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های انجام شده'
    )
    remaining_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های باقیمانده'
    )
    
    # زمان‌ها
    average_visit_duration = models.PositiveIntegerField(
        default=0,
        verbose_name='میانگین زمان ویزیت (دقیقه)'
    )
    estimated_wait_time = models.PositiveIntegerField(
        default=0,
        verbose_name='تخمین زمان انتظار (دقیقه)'
    )
    
    # وضعیت پزشک
    is_doctor_available = models.BooleanField(
        default=True,
        verbose_name='پزشک حاضر'
    )
    doctor_break_until = models.TimeField(
        blank=True,
        null=True,
        verbose_name='استراحت تا'
    )
    
    # تاریخ‌ها
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='شروع کار'
    )
    last_update = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    class Meta:
        db_table = 'queue_status'
        verbose_name = 'وضعیت صف'
        verbose_name_plural = 'وضعیت صف‌ها'
        unique_together = ['doctor', 'clinic', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.clinic.name} - {self.date}"
    
    def get_ahead_count(self, queue_number):
        """تعداد افراد جلوتر"""
        if queue_number <= self.current_queue_number:
            return 0
        return queue_number - self.current_queue_number - 1
    
    def calculate_estimated_wait(self, queue_number):
        """محاسبه تخمین زمان انتظار"""
        ahead = self.get_ahead_count(queue_number)
        avg_duration = self.average_visit_duration or self.doctor.visit_duration
        return ahead * avg_duration


class QueueLog(models.Model):
    """
    مدل لاگ تغییرات صف
    """
    
    ACTION_CHOICES = [
        ('call_next', 'فراخوانی نفر بعدی'),
        ('complete', 'پایان ویزیت'),
        ('skip', 'رد شدن'),
        ('recall', 'فراخوانی مجدد'),
        ('break_start', 'شروع استراحت'),
        ('break_end', 'پایان استراحت'),
        ('day_start', 'شروع کار'),
        ('day_end', 'پایان کار'),
    ]
    
    queue_status = models.ForeignKey(
        QueueStatus,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='صف'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='عملیات'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='نوبت'
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='انجام توسط'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ'
    )
    
    class Meta:
        db_table = 'queue_log'
        verbose_name = 'لاگ صف'
        verbose_name_plural = 'لاگ‌های صف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.queue_status} - {self.get_action_display()}"


class QueueAnnouncement(models.Model):
    """
    مدل اعلان‌های صف (برای نمایش در صفحه صف زنده)
    """
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='queue_announcements',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='queue_announcements',
        verbose_name='مرکز'
    )
    message = models.TextField(
        verbose_name='پیام'
    )
    is_global = models.BooleanField(
        default=False,
        verbose_name='نمایش در همه صف‌ها'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name='اولویت'
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ شروع'
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ پایان'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'queue_announcement'
        verbose_name = 'اعلان صف'
        verbose_name_plural = 'اعلان‌های صف'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.message[:50]

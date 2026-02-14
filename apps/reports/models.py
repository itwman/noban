"""
مدل‌های اپلیکیشن گزارش‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings


class DailyReport(models.Model):
    """
    مدل گزارش روزانه
    """
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='daily_reports',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='daily_reports',
        verbose_name='مرکز'
    )
    date = models.DateField(
        verbose_name='تاریخ'
    )
    
    # آمار نوبت‌ها
    total_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='کل نوبت‌ها'
    )
    completed_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های انجام شده'
    )
    cancelled_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های لغو شده'
    )
    no_show_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='عدم حضور'
    )
    new_patients = models.PositiveIntegerField(
        default=0,
        verbose_name='بیماران جدید'
    )
    
    # آمار مالی
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='درآمد کل'
    )
    online_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='درآمد آنلاین'
    )
    cash_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='درآمد نقدی'
    )
    refunded_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ بازپرداخت'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        db_table = 'reports_daily_report'
        verbose_name = 'گزارش روزانه'
        verbose_name_plural = 'گزارش‌های روزانه'
        ordering = ['-date']
        unique_together = ['doctor', 'clinic', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['doctor', 'date']),
            models.Index(fields=['clinic', 'date']),
        ]
    
    def __str__(self):
        parts = [str(self.date)]
        if self.doctor:
            parts.append(self.doctor.user.get_full_name())
        if self.clinic:
            parts.append(self.clinic.name)
        return ' - '.join(parts)
    
    def get_completion_rate(self):
        """درصد تکمیل نوبت‌ها"""
        if self.total_appointments == 0:
            return 0
        return round(self.completed_appointments / self.total_appointments * 100, 1)
    
    def get_cancellation_rate(self):
        """درصد لغو نوبت‌ها"""
        if self.total_appointments == 0:
            return 0
        return round(self.cancelled_appointments / self.total_appointments * 100, 1)


class MonthlyReport(models.Model):
    """
    مدل گزارش ماهانه
    """
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='monthly_reports',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='monthly_reports',
        verbose_name='مرکز'
    )
    year = models.PositiveIntegerField(
        verbose_name='سال'
    )
    month = models.PositiveIntegerField(
        verbose_name='ماه'
    )
    
    # آمار نوبت‌ها
    total_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='کل نوبت‌ها'
    )
    completed_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های انجام شده'
    )
    cancelled_appointments = models.PositiveIntegerField(
        default=0,
        verbose_name='نوبت‌های لغو شده'
    )
    new_patients = models.PositiveIntegerField(
        default=0,
        verbose_name='بیماران جدید'
    )
    unique_patients = models.PositiveIntegerField(
        default=0,
        verbose_name='بیماران یکتا'
    )
    
    # آمار مالی
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name='درآمد کل'
    )
    online_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name='درآمد آنلاین'
    )
    average_daily_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='میانگین درآمد روزانه'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        db_table = 'reports_monthly_report'
        verbose_name = 'گزارش ماهانه'
        verbose_name_plural = 'گزارش‌های ماهانه'
        ordering = ['-year', '-month']
        unique_together = ['doctor', 'clinic', 'year', 'month']
    
    def __str__(self):
        parts = [f"{self.year}/{self.month:02d}"]
        if self.doctor:
            parts.append(self.doctor.user.get_full_name())
        if self.clinic:
            parts.append(self.clinic.name)
        return ' - '.join(parts)


class FinancialSummary(models.Model):
    """
    مدل خلاصه مالی (برای داشبورد)
    """
    
    PERIOD_CHOICES = [
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('yearly', 'سالانه'),
    ]
    
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='مرکز'
    )
    period_type = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        verbose_name='نوع دوره'
    )
    start_date = models.DateField(
        verbose_name='تاریخ شروع'
    )
    end_date = models.DateField(
        verbose_name='تاریخ پایان'
    )
    
    total_income = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name='کل درآمد'
    )
    total_refunds = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name='کل بازپرداخت'
    )
    net_income = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        default=0,
        verbose_name='درآمد خالص'
    )
    transaction_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد تراکنش'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'reports_financial_summary'
        verbose_name = 'خلاصه مالی'
        verbose_name_plural = 'خلاصه‌های مالی'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.get_period_type_display()} - {self.start_date}"


class ExportedReport(models.Model):
    """
    مدل گزارش‌های خروجی گرفته شده
    """
    
    FORMAT_CHOICES = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
    ]
    
    TYPE_CHOICES = [
        ('appointments', 'نوبت‌ها'),
        ('financial', 'مالی'),
        ('patients', 'بیماران'),
        ('doctors', 'پزشکان'),
        ('custom', 'سفارشی'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exported_reports',
        verbose_name='کاربر'
    )
    report_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='نوع گزارش'
    )
    file_format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name='فرمت فایل'
    )
    file = models.FileField(
        upload_to='reports/exports/',
        verbose_name='فایل'
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name='حجم فایل'
    )
    filters_applied = models.JSONField(
        blank=True,
        null=True,
        verbose_name='فیلترهای اعمال شده'
    )
    rows_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد سطرها'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ انقضا'
    )
    
    class Meta:
        db_table = 'reports_exported_report'
        verbose_name = 'گزارش خروجی'
        verbose_name_plural = 'گزارش‌های خروجی'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at}"

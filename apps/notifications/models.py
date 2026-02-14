"""
مدل‌های اپلیکیشن اعلان‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings


class SMS(models.Model):
    """
    مدل پیامک
    """
    
    STATUS_CHOICES = [
        ('pending', 'در صف ارسال'),
        ('sent', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
        ('failed', 'ناموفق'),
    ]
    
    TEMPLATE_CHOICES = [
        ('appointment_confirm', 'تأیید نوبت'),
        ('appointment_reminder', 'یادآوری نوبت'),
        ('appointment_cancelled', 'لغو نوبت'),
        ('queue_update', 'بروزرسانی صف'),
        ('payment_success', 'تأیید پرداخت'),
        ('verification_code', 'کد تأیید'),
        ('welcome', 'خوش‌آمدگویی'),
        ('custom', 'سفارشی'),
    ]
    
    receptor = models.CharField(
        max_length=11,
        verbose_name='شماره گیرنده'
    )
    message = models.TextField(
        verbose_name='متن پیامک'
    )
    template = models.CharField(
        max_length=50,
        choices=TEMPLATE_CHOICES,
        blank=True,
        null=True,
        verbose_name='الگو'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # اطلاعات ارسال
    message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شناسه پیامک'
    )
    cost = models.PositiveIntegerField(
        default=0,
        verbose_name='هزینه (ریال)'
    )
    
    # خطا
    error_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='کد خطا'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='پیام خطا'
    )
    
    # مدل مرتبط
    related_model = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='مدل مرتبط'
    )
    related_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='شناسه مرتبط'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ ارسال'
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ تحویل'
    )
    
    class Meta:
        db_table = 'notifications_sms'
        verbose_name = 'پیامک'
        verbose_name_plural = 'پیامک‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receptor']),
            models.Index(fields=['status']),
            models.Index(fields=['template']),
            models.Index(fields=['related_model', 'related_id']),
        ]
    
    def __str__(self):
        return f"{self.receptor} - {self.get_template_display() or 'سفارشی'}"
    
    def is_sent(self):
        return self.status in ['sent', 'delivered']


class SMSTemplate(models.Model):
    """
    مدل الگوهای پیامک
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='نام الگو'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='عنوان'
    )
    content = models.TextField(
        verbose_name='محتوای پیامک',
        help_text='از متغیرها استفاده کنید: {patient_name}, {doctor_name}, {date}, {time}, {queue_number}, {clinic_name}'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        db_table = 'notifications_sms_template'
        verbose_name = 'الگوی پیامک'
        verbose_name_plural = 'الگوهای پیامک'
        ordering = ['name']
    
    def __str__(self):
        return self.title


class SMSSetting(models.Model):
    """
    مدل تنظیمات پیامک
    """
    
    # sms.ir
    api_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='API Key'
    )
    line_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='شماره خط'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='فعال'
    )
    
    # تنظیمات ارسال
    send_appointment_confirm = models.BooleanField(
        default=True,
        verbose_name='ارسال تأیید نوبت'
    )
    send_appointment_reminder = models.BooleanField(
        default=True,
        verbose_name='ارسال یادآوری'
    )
    reminder_hours_before = models.PositiveIntegerField(
        default=24,
        verbose_name='ساعت قبل از یادآوری'
    )
    send_queue_update = models.BooleanField(
        default=True,
        verbose_name='ارسال بروزرسانی صف'
    )
    send_cancel_notification = models.BooleanField(
        default=True,
        verbose_name='ارسال اعلان لغو'
    )
    max_daily_sms = models.PositiveIntegerField(
        default=1000,
        verbose_name='حداکثر پیامک روزانه'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    class Meta:
        db_table = 'notifications_sms_setting'
        verbose_name = 'تنظیمات پیامک'
        verbose_name_plural = 'تنظیمات پیامک'
    
    def __str__(self):
        return 'تنظیمات پیامک'
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Notification(models.Model):
    """
    مدل اعلان‌های داخلی
    """
    
    TYPE_CHOICES = [
        ('info', 'اطلاعات'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('danger', 'خطر'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='کاربر'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان'
    )
    message = models.TextField(
        verbose_name='پیام'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name='نوع'
    )
    link = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='لینک'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='خوانده شده'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ خواندن'
    )
    
    class Meta:
        db_table = 'notifications_notification'
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"

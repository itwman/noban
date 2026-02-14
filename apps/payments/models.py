"""
مدل‌های اپلیکیشن پرداخت - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings
import uuid


class Transaction(models.Model):
    """
    مدل تراکنش پرداخت
    """
    
    GATEWAY_CHOICES = [
        ('zarinpal', 'زرین‌پال'),
        ('drik', 'دریک'),
        ('cash', 'نقدی'),
        ('card', 'کارت‌خوان'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('paid', 'پرداخت شده'),
        ('verified', 'تأیید شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازپرداخت شده'),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('full_payment', 'پرداخت کامل'),
        ('deposit', 'بیعانه'),
        ('remaining', 'مابقی'),
        ('refund', 'بازپرداخت'),
    ]
    
    # شناسه یکتا
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='شناسه یکتا'
    )
    
    # روابط
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='نوبت'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='کاربر'
    )
    
    # اطلاعات مالی
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='مبلغ (تومان)'
    )
    gateway = models.CharField(
        max_length=20,
        choices=GATEWAY_CHOICES,
        verbose_name='درگاه'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        default='full_payment',
        verbose_name='نوع تراکنش'
    )
    
    # اطلاعات درگاه
    authority = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Authority'
    )
    ref_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شماره پیگیری'
    )
    card_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='شماره کارت'
    )
    card_hash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='هش کارت'
    )
    
    # وضعیت
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # توضیحات
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
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
    
    # اطلاعات فنی
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='آدرس IP'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    callback_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='داده‌های Callback'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ پرداخت'
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ تأیید'
    )
    
    class Meta:
        db_table = 'payments_transaction'
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['authority']),
            models.Index(fields=['ref_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"{self.uuid} - {self.amount} تومان - {self.get_status_display()}"
    
    def is_successful(self):
        """آیا تراکنش موفق بوده؟"""
        return self.status in ['paid', 'verified']
    
    def can_verify(self):
        """آیا قابل تأیید است؟"""
        return self.status == 'paid' and self.authority
    
    def get_gateway_display_fa(self):
        """نام فارسی درگاه"""
        gateway_dict = dict(self.GATEWAY_CHOICES)
        return gateway_dict.get(self.gateway, self.gateway)


class Refund(models.Model):
    """
    مدل بازپرداخت
    """
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'انجام شده'),
        ('failed', 'ناموفق'),
        ('rejected', 'رد شده'),
    ]
    
    REASON_CHOICES = [
        ('cancelled', 'لغو نوبت'),
        ('duplicate', 'پرداخت تکراری'),
        ('error', 'خطای سیستم'),
        ('customer_request', 'درخواست مشتری'),
        ('other', 'سایر'),
    ]
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='refunds',
        verbose_name='تراکنش اصلی'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='مبلغ بازپرداخت'
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='cancelled',
        verbose_name='دلیل'
    )
    reason_detail = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    ref_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شماره پیگیری بازپرداخت'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='پردازش توسط'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ درخواست'
    )
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='تاریخ پردازش'
    )
    
    class Meta:
        db_table = 'payments_refund'
        verbose_name = 'بازپرداخت'
        verbose_name_plural = 'بازپرداخت‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"بازپرداخت {self.amount} تومان - {self.transaction}"


class PaymentSetting(models.Model):
    """
    مدل تنظیمات پرداخت
    """
    
    # زرین‌پال
    zarinpal_merchant_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Merchant ID زرین‌پال'
    )
    zarinpal_sandbox = models.BooleanField(
        default=True,
        verbose_name='حالت تست زرین‌پال'
    )
    zarinpal_active = models.BooleanField(
        default=False,
        verbose_name='زرین‌پال فعال'
    )
    
    # دریک
    drik_api_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='API Key دریک'
    )
    drik_sandbox = models.BooleanField(
        default=True,
        verbose_name='حالت تست دریک'
    )
    drik_active = models.BooleanField(
        default=False,
        verbose_name='دریک فعال'
    )
    
    # تنظیمات عمومی
    default_gateway = models.CharField(
        max_length=20,
        choices=[('zarinpal', 'زرین‌پال'), ('drik', 'دریک')],
        default='zarinpal',
        verbose_name='درگاه پیش‌فرض'
    )
    min_payment_amount = models.PositiveIntegerField(
        default=1000,
        verbose_name='حداقل مبلغ پرداخت'
    )
    allow_deposit = models.BooleanField(
        default=True,
        verbose_name='امکان پرداخت بیعانه'
    )
    allow_cash = models.BooleanField(
        default=True,
        verbose_name='امکان پرداخت نقدی'
    )
    
    # تاریخ‌ها
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    
    class Meta:
        db_table = 'payments_setting'
        verbose_name = 'تنظیمات پرداخت'
        verbose_name_plural = 'تنظیمات پرداخت'
    
    def __str__(self):
        return 'تنظیمات پرداخت'
    
    @classmethod
    def get_settings(cls):
        """دریافت تنظیمات (ایجاد اگر وجود ندارد)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

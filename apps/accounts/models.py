"""
مدل‌های اپلیکیشن کاربران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    مدیر سفارشی برای مدل کاربر
    """
    
    def create_user(self, phone, password=None, **extra_fields):
        """
        ایجاد کاربر عادی
        """
        if not phone:
            raise ValueError('شماره موبایل الزامی است')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """
        ایجاد سوپر یوزر
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'superadmin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپر یوزر باید is_staff=True باشد')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپر یوزر باید is_superuser=True باشد')
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    مدل کاربر سفارشی با شماره موبایل به عنوان نام کاربری
    """
    
    ROLE_CHOICES = [
        ('superadmin', 'مدیر کل'),
        ('doctor', 'پزشک'),
        ('secretary', 'منشی'),
        ('staff', 'کارمند'),
        ('patient', 'بیمار'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
        ('other', 'سایر'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
    )
    
    national_code_regex = RegexValidator(
        regex=r'^\d{10}$',
        message='کد ملی باید 10 رقم باشد'
    )
    
    # فیلدهای اصلی
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_regex],
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='ایمیل'
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name='نام'
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name='نام خانوادگی'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient',
        verbose_name='نقش'
    )
    
    # اطلاعات تکمیلی
    national_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[national_code_regex],
        verbose_name='کد ملی'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='جنسیت'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='نشانی'
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    
    # وضعیت‌ها
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='دسترسی پنل مدیریت'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تأیید شده'
    )
    
    # تاریخ‌ها
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ عضویت'
    )
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='آخرین ورود'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['role']),
            models.Index(fields=['national_code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone})"
    
    def get_full_name(self):
        """برگرداندن نام کامل"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """برگرداندن نام کوتاه"""
        return self.first_name
    
    def get_role_display_fa(self):
        """برگرداندن نام فارسی نقش"""
        role_dict = dict(self.ROLE_CHOICES)
        return role_dict.get(self.role, self.role)
    
    def is_doctor(self):
        return self.role == 'doctor'
    
    def is_secretary(self):
        return self.role == 'secretary'
    
    def is_patient(self):
        return self.role == 'patient'
    
    def is_admin(self):
        return self.role == 'superadmin' or self.is_superuser


class VerificationCode(models.Model):
    """
    مدل کد تأیید (OTP)
    """
    
    CODE_TYPES = [
        ('register', 'ثبت‌نام'),
        ('login', 'ورود'),
        ('password_reset', 'بازیابی رمز'),
    ]
    
    phone = models.CharField(
        max_length=11,
        verbose_name='شماره موبایل'
    )
    code = models.CharField(
        max_length=6,
        verbose_name='کد تأیید'
    )
    code_type = models.CharField(
        max_length=20,
        choices=CODE_TYPES,
        default='login',
        verbose_name='نوع کد'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='استفاده شده'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    expires_at = models.DateTimeField(
        verbose_name='تاریخ انقضا'
    )
    
    class Meta:
        db_table = 'accounts_verification_code'
        verbose_name = 'کد تأیید'
        verbose_name_plural = 'کدهای تأیید'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone} - {self.code}"
    
    def is_valid(self):
        """بررسی معتبر بودن کد"""
        return not self.is_used and self.expires_at > timezone.now()


class UserSession(models.Model):
    """
    مدل نشست‌های کاربر
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='کاربر'
    )
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='کلید نشست'
    )
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
    device_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='نوع دستگاه'
    )
    browser = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='مرورگر'
    )
    os = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='سیستم عامل'
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='موقعیت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین فعالیت'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    class Meta:
        db_table = 'accounts_user_session'
        verbose_name = 'نشست کاربر'
        verbose_name_plural = 'نشست‌های کاربران'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.phone} - {self.device_type or 'نامشخص'}"


class AuditLog(models.Model):
    """
    مدل لاگ تغییرات (Audit Log)
    """
    
    ACTION_TYPES = [
        ('create', 'ایجاد'),
        ('update', 'ویرایش'),
        ('delete', 'حذف'),
        ('login', 'ورود'),
        ('logout', 'خروج'),
        ('password_change', 'تغییر رمز'),
        ('other', 'سایر'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='کاربر'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name='عملیات'
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='نام مدل'
    )
    object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='شناسه شیء'
    )
    object_repr = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='نمایش شیء'
    )
    changes = models.JSONField(
        blank=True,
        null=True,
        verbose_name='تغییرات'
    )
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ'
    )
    
    class Meta:
        db_table = 'accounts_audit_log'
        verbose_name = 'لاگ تغییرات'
        verbose_name_plural = 'لاگ‌های تغییرات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        user_str = self.user.phone if self.user else 'ناشناس'
        return f"{user_str} - {self.get_action_display()} - {self.created_at}"

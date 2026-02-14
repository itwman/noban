"""
مدل‌های اپلیکیشن مراکز پزشکی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


class Clinic(models.Model):
    """
    مدل مرکز پزشکی / مطب / کلینیک / بیمارستان
    """
    
    CLINIC_TYPES = [
        ('office', 'مطب شخصی'),
        ('clinic', 'کلینیک'),
        ('hospital', 'بیمارستان'),
        ('center', 'مرکز درمانی'),
        ('laboratory', 'آزمایشگاه'),
        ('imaging', 'مرکز تصویربرداری'),
    ]
    
    phone_regex = RegexValidator(
        regex=r'^\d{11}$',
        message='شماره تلفن باید 11 رقم باشد'
    )
    
    postal_code_regex = RegexValidator(
        regex=r'^\d{10}$',
        message='کد پستی باید 10 رقم باشد'
    )
    
    # نوع و مالکیت
    clinic_type = models.CharField(
        max_length=20,
        choices=CLINIC_TYPES,
        default='office',
        verbose_name='نوع مرکز'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='owned_clinics',
        verbose_name='مالک/ایجاد کننده'
    )
    
    # اطلاعات اصلی
    name = models.CharField(
        max_length=200,
        verbose_name='نام مرکز'
    )
    phone = models.CharField(
        max_length=11,
        validators=[phone_regex],
        verbose_name='تلفن'
    )
    mobile = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='موبایل'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='ایمیل'
    )
    
    # نشانی
    province = models.CharField(
        max_length=50,
        verbose_name='استان'
    )
    city = models.CharField(
        max_length=50,
        verbose_name='شهر'
    )
    address = models.TextField(
        verbose_name='نشانی کامل'
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[postal_code_regex],
        verbose_name='کد پستی'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='عرض جغرافیایی'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='طول جغرافیایی'
    )
    
    # اطلاعات تکمیلی
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    logo = models.ImageField(
        upload_to='clinics/logos/',
        blank=True,
        null=True,
        verbose_name='لوگو'
    )
    license_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='شماره مجوز'
    )
    
    # تنظیمات
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='عمومی (قابل مشاهده برای همه)'
    )
    allows_online_booking = models.BooleanField(
        default=True,
        verbose_name='امکان رزرو آنلاین'
    )
    requires_payment = models.BooleanField(
        default=False,
        verbose_name='نیاز به پرداخت'
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
        db_table = 'clinics_clinic'
        verbose_name = 'مرکز پزشکی'
        verbose_name_plural = 'مراکز پزشکی'
        ordering = ['name']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['province']),
            models.Index(fields=['is_active']),
            models.Index(fields=['clinic_type']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"{self.get_clinic_type_display()} {self.name}"
    
    def get_full_address(self):
        """برگرداندن نشانی کامل"""
        return f"{self.province}، {self.city}، {self.address}"
    
    def get_type_icon(self):
        """آیکون نوع مرکز"""
        icons = {
            'office': 'fa-clinic-medical',
            'clinic': 'fa-hospital-user',
            'hospital': 'fa-hospital',
            'center': 'fa-building',
            'laboratory': 'fa-flask',
            'imaging': 'fa-x-ray',
        }
        return icons.get(self.clinic_type, 'fa-hospital')
    
    def get_type_color(self):
        """رنگ نوع مرکز"""
        colors = {
            'office': 'success',
            'clinic': 'primary',
            'hospital': 'danger',
            'center': 'info',
            'laboratory': 'warning',
            'imaging': 'secondary',
        }
        return colors.get(self.clinic_type, 'secondary')


class ClinicImage(models.Model):
    """
    مدل تصاویر مرکز پزشکی
    """
    
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='مرکز'
    )
    image = models.ImageField(
        upload_to='clinics/images/',
        verbose_name='تصویر'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='عنوان'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='تصویر اصلی'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ آپلود'
    )
    
    class Meta:
        db_table = 'clinics_clinic_image'
        verbose_name = 'تصویر مرکز'
        verbose_name_plural = 'تصاویر مراکز'
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        return f"{self.clinic.name} - {self.title or 'تصویر'}"

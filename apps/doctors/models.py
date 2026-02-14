"""
مدل‌های اپلیکیشن پزشکان - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Doctor(models.Model):
    """
    مدل پزشک
    """
    
    # ارتباط با کاربر
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name='کاربر'
    )
    
    # اطلاعات حرفه‌ای
    specialization = models.CharField(
        max_length=100,
        verbose_name='تخصص'
    )
    medical_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='کد نظام پزشکی'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='بیوگرافی'
    )
    education = models.TextField(
        blank=True,
        null=True,
        verbose_name='تحصیلات'
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name='سال‌های تجربه'
    )
    
    # تصویر
    profile_image = models.ImageField(
        upload_to='doctors/profiles/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    
    # تنظیمات نوبت‌دهی
    visit_duration = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(120)],
        verbose_name='مدت ویزیت (دقیقه)'
    )
    gap_between_visits = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        verbose_name='فاصله بین نوبت‌ها (دقیقه)'
    )
    max_daily_appointments = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='حداکثر نوبت روزانه'
    )
    max_advance_days = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        verbose_name='حداکثر روزهای رزرو آینده'
    )
    min_cancel_hours = models.PositiveIntegerField(
        default=24,
        verbose_name='حداقل ساعت لغو نوبت'
    )
    
    # تنظیمات مالی
    visit_fee = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='هزینه ویزیت (تومان)'
    )
    deposit_percent = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='درصد بیعانه'
    )
    
    # وضعیت
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='ویژه'
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
        db_table = 'doctors_doctor'
        verbose_name = 'پزشک'
        verbose_name_plural = 'پزشکان'
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['medical_code']),
            models.Index(fields=['specialization']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"دکتر {self.user.get_full_name()} - {self.specialization}"
    
    def get_full_title(self):
        """برگرداندن عنوان کامل پزشک"""
        return f"دکتر {self.user.get_full_name()}"
    
    def get_time_slot_duration(self):
        """برگرداندن طول هر تایم (ویزیت + فاصله)"""
        return self.visit_duration + self.gap_between_visits
    
    def get_deposit_amount(self):
        """محاسبه مبلغ بیعانه"""
        return int(self.visit_fee * self.deposit_percent / 100)


class DoctorClinic(models.Model):
    """
    مدل ارتباط پزشک با مرکز پزشکی
    """
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='clinics',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='doctors',
        verbose_name='مرکز'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='مرکز اصلی'
    )
    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='شماره اتاق'
    )
    
    # تنظیمات اختصاصی این مرکز (اختیاری - اگر خالی باشد از تنظیمات پزشک استفاده می‌شود)
    custom_visit_fee = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='هزینه ویزیت سفارشی'
    )
    custom_visit_duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='مدت ویزیت سفارشی'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'doctors_doctor_clinic'
        verbose_name = 'ارتباط پزشک-مرکز'
        verbose_name_plural = 'ارتباطات پزشک-مرکز'
        unique_together = ['doctor', 'clinic']
        indexes = [
            models.Index(fields=['doctor', 'clinic']),
        ]
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.clinic.name}"
    
    def get_visit_fee(self):
        """دریافت هزینه ویزیت (سفارشی یا پیش‌فرض)"""
        return self.custom_visit_fee or self.doctor.visit_fee
    
    def get_visit_duration(self):
        """دریافت مدت ویزیت (سفارشی یا پیش‌فرض)"""
        return self.custom_visit_duration or self.doctor.visit_duration


class WorkSchedule(models.Model):
    """
    مدل تقویم کاری پزشک
    """
    
    DAYS_OF_WEEK = [
        (0, 'شنبه'),
        (1, 'یکشنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنج‌شنبه'),
        (6, 'جمعه'),
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='schedules',
        blank=True,
        null=True,
        verbose_name='مرکز'
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name='روز هفته'
    )
    start_time = models.TimeField(
        verbose_name='ساعت شروع'
    )
    end_time = models.TimeField(
        verbose_name='ساعت پایان'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    max_appointments = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='حداکثر نوبت (اختیاری)'
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
        db_table = 'doctors_work_schedule'
        verbose_name = 'تقویم کاری'
        verbose_name_plural = 'تقویم کاری'
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['doctor', 'day_of_week']),
            models.Index(fields=['clinic', 'day_of_week']),
        ]
    
    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK).get(self.day_of_week)
        return f"{self.doctor.user.get_full_name()} - {day_name} ({self.start_time} - {self.end_time})"
    
    def get_day_name(self):
        """برگرداندن نام روز"""
        return dict(self.DAYS_OF_WEEK).get(self.day_of_week)


class DoctorHoliday(models.Model):
    """
    مدل تعطیلات و مرخصی‌های پزشک
    """
    
    HOLIDAY_TYPES = [
        ('holiday', 'تعطیل'),
        ('vacation', 'مرخصی'),
        ('emergency', 'اضطراری'),
        ('other', 'سایر'),
    ]
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='holidays',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='doctor_holidays',
        verbose_name='مرکز (خالی = همه مراکز)'
    )
    date = models.DateField(
        verbose_name='تاریخ'
    )
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPES,
        default='holiday',
        verbose_name='نوع'
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='دلیل'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'doctors_doctor_holiday'
        verbose_name = 'تعطیلی پزشک'
        verbose_name_plural = 'تعطیلات پزشکان'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['doctor', 'date']),
        ]
    
    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.date}"


class ServiceType(models.Model):
    """
    انواع خدمات پزشکی
    ویزیت، سونوگرافی، آزمایشگاه، نوار قلب، تزریقات، مشاوره، جراحی سرپایی، فیزیوتراپی
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='نام خدمت'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name='شناسه یکتا'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='توضیحات'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='آیکون (FontAwesome)'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='پیش‌فرض سیستم',
        help_text='خدمات پیش‌فرض توسط سیستم ایجاد شده و قابل حذف نیستند'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
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
        db_table = 'doctors_servicetype'
        ordering = ['sort_order', 'name']
        verbose_name = 'نوع خدمت'
        verbose_name_plural = 'انواع خدمات'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name


class InsuranceType(models.Model):
    """
    انواع بیمه
    آزاد، تأمین اجتماعی، خدمات درمانی، نیروهای مسلح، سلامت ایرانیان، بیمه تکمیلی، سایر
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='نام بیمه'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name='شناسه یکتا'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='توضیحات'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='آیکون'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='پیش‌فرض سیستم',
        help_text='بیمه‌های پیش‌فرض توسط سیستم ایجاد شده و قابل حذف نیستند'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
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
        db_table = 'doctors_insurancetype'
        ordering = ['sort_order', 'name']
        verbose_name = 'نوع بیمه'
        verbose_name_plural = 'انواع بیمه'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        return self.name


class DoctorTariff(models.Model):
    """
    تعرفه‌های پزشک
    ماتریس: پزشک × خدمت × بیمه × مرکز = مبلغ
    اگر clinic_id = NULL باشد، تعرفه عمومی برای همه مراکز است
    تعرفه اختصاصی مرکز اولویت دارد بر تعرفه عمومی
    """
    
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='tariffs',
        verbose_name='پزشک'
    )
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='tariffs',
        blank=True,
        null=True,
        verbose_name='مرکز',
        help_text='خالی = تعرفه عمومی برای همه مراکز'
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.RESTRICT,
        related_name='tariffs',
        verbose_name='نوع خدمت'
    )
    insurance_type = models.ForeignKey(
        InsuranceType,
        on_delete=models.RESTRICT,
        related_name='tariffs',
        verbose_name='نوع بیمه'
    )
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ تعرفه (ریال)'
    )
    deposit_required = models.BooleanField(
        default=False,
        verbose_name='نیاز به بیعانه'
    )
    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ بیعانه (ریال)',
        help_text='اگر صفر باشد از درصد بیعانه استفاده می‌شود'
    )
    deposit_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='درصد بیعانه',
        help_text='اگر مبلغ بیعانه صفر باشد، از این درصد استفاده می‌شود'
    )
    online_payment_required = models.BooleanField(
        default=False,
        verbose_name='الزام پرداخت آنلاین'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='توضیحات تعرفه'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
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
        db_table = 'doctors_doctortariff'
        ordering = ['service_type__sort_order', 'insurance_type__sort_order']
        verbose_name = 'تعرفه پزشک'
        verbose_name_plural = 'تعرفه‌های پزشک'
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'clinic', 'service_type', 'insurance_type'],
                name='unique_tariff'
            )
        ]
        indexes = [
            models.Index(fields=['doctor', 'clinic']),
            models.Index(fields=['doctor', 'is_active']),
            models.Index(fields=['service_type']),
            models.Index(fields=['insurance_type']),
        ]
    
    def __str__(self):
        clinic_name = self.clinic.name if self.clinic else 'همه مراکز'
        return (
            f"{self.doctor} - {self.service_type} - "
            f"{self.insurance_type} - {clinic_name}: "
            f"{self.fee:,.0f} ریال"
        )
    
    def get_deposit_amount(self):
        """محاسبه مبلغ بیعانه"""
        if not self.deposit_required:
            return 0
        if self.deposit_amount > 0:
            return int(self.deposit_amount)
        if self.deposit_percent > 0:
            return int(self.fee * self.deposit_percent / 100)
        return 0
    
    def get_fee_display(self):
        """نمایش مبلغ تعرفه با فرمت"""
        return f"{self.fee:,.0f}"
    
    def get_deposit_display(self):
        """نمایش مبلغ بیعانه با فرمت"""
        amount = self.get_deposit_amount()
        return f"{amount:,.0f}" if amount > 0 else '-'


class Specialization(models.Model):
    """
    مدل تخصص‌های پزشکی (برای مدیریت بهتر)
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='نام تخصص'
    )
    name_en = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='نام انگلیسی'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='آیکون (FontAwesome)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب'
    )
    
    class Meta:
        db_table = 'doctors_specialization'
        verbose_name = 'تخصص'
        verbose_name_plural = 'تخصص‌ها'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

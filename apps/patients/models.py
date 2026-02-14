"""
مدل‌های اپلیکیشن بیماران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from django.conf import settings
import os


def medical_file_upload_path(instance, filename):
    """تولید مسیر آپلود فایل‌های پزشکی"""
    ext = filename.split('.')[-1]
    patient_id = instance.record.patient.id
    return f'medical_files/patient_{patient_id}/{instance.file_type}/{filename}'


class MedicalRecord(models.Model):
    """
    مدل پرونده پزشکی
    """
    
    # روابط
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name='بیمار'
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name='پزشک'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records',
        verbose_name='نوبت مرتبط'
    )
    
    # اطلاعات پزشکی
    chief_complaint = models.TextField(
        blank=True,
        null=True,
        verbose_name='شکایت اصلی'
    )
    history_of_present_illness = models.TextField(
        blank=True,
        null=True,
        verbose_name='شرح حال بیماری'
    )
    physical_examination = models.TextField(
        blank=True,
        null=True,
        verbose_name='معاینه فیزیکی'
    )
    diagnosis = models.TextField(
        blank=True,
        null=True,
        verbose_name='تشخیص'
    )
    prescription = models.TextField(
        blank=True,
        null=True,
        verbose_name='نسخه / درمان'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت‌ها'
    )
    
    # علائم حیاتی
    blood_pressure = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='فشار خون'
    )
    pulse_rate = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='ضربان قلب'
    )
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name='دما (سلسیوس)'
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='وزن (کیلوگرم)'
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='قد (سانتی‌متر)'
    )
    
    # پیگیری
    next_visit_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ مراجعه بعدی'
    )
    follow_up_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت پیگیری'
    )
    
    # تاریخ‌ها
    visit_date = models.DateField(
        verbose_name='تاریخ ویزیت'
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
        db_table = 'patients_medical_record'
        verbose_name = 'پرونده پزشکی'
        verbose_name_plural = 'پرونده‌های پزشکی'
        ordering = ['-visit_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['doctor', 'created_at']),
            models.Index(fields=['visit_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_title()} - {self.visit_date}"
    
    def get_bmi(self):
        """محاسبه BMI"""
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None
    
    @property
    def prescription_items_by_type(self):
        """دسته‌بندی آیتم‌های تجویز بر اساس نوع"""
        items = self.prescription_items.all()
        return {
            'medication': [i for i in items if i.item_type == 'medication'],
            'lab_test': [i for i in items if i.item_type == 'lab_test'],
            'imaging': [i for i in items if i.item_type == 'imaging'],
            'procedure': [i for i in items if i.item_type == 'procedure'],
        }


class MedicalFile(models.Model):
    """
    مدل فایل‌های پزشکی
    """
    
    FILE_TYPE_CHOICES = [
        ('image', 'تصویر'),
        ('pdf', 'PDF'),
        ('lab_result', 'نتیجه آزمایش'),
        ('xray', 'رادیولوژی'),
        ('scan', 'سی‌تی اسکن/MRI'),
        ('ecg', 'نوار قلب'),
        ('prescription', 'نسخه'),
        ('other', 'سایر'),
    ]
    
    record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='پرونده'
    )
    file = models.FileField(
        upload_to=medical_file_upload_path,
        verbose_name='فایل'
    )
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='other',
        verbose_name='نوع فایل'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='عنوان'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='حجم (بایت)'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='آپلود توسط'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ آپلود'
    )
    
    class Meta:
        db_table = 'patients_medical_file'
        verbose_name = 'فایل پزشکی'
        verbose_name_plural = 'فایل‌های پزشکی'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.record.patient.get_full_name()} - {self.title or self.get_file_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    def get_file_extension(self):
        """دریافت پسوند فایل"""
        if self.file:
            name, extension = os.path.splitext(self.file.name)
            return extension.lower()
        return ''
    
    def get_file_size_display(self):
        """نمایش حجم فایل به صورت خوانا"""
        if not self.file_size:
            return '-'
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class PatientNote(models.Model):
    """
    مدل یادداشت‌های عمومی بیمار
    """
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_notes',
        verbose_name='بیمار'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_patient_notes',
        verbose_name='ایجاد توسط'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان'
    )
    content = models.TextField(
        verbose_name='محتوا'
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name='مهم'
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name='خصوصی'
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
        db_table = 'patients_patient_note'
        verbose_name = 'یادداشت بیمار'
        verbose_name_plural = 'یادداشت‌های بیماران'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.title}"


class MedicalTerm(models.Model):
    """
    مدل اصطلاحات پزشکی (علائم، تشخیص‌ها، داروها)
    پزشکان هنگام ثبت پرونده از این جدول autocomplete دریافت می‌کنند
    و می‌توانند موارد جدید هم اضافه کنند.
    """
    
    CATEGORY_CHOICES = [
        ('symptom', 'علامت / شکایت'),
        ('diagnosis', 'تشخیص'),
        ('medication', 'دارو'),
        ('lab_test', 'آزمایش'),
        ('imaging', 'تصویربرداری'),
        ('procedure', 'اقدام درمانی'),
    ]
    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='دسته‌بندی',
        db_index=True
    )
    name_fa = models.CharField(
        max_length=200,
        verbose_name='نام فارسی'
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='نام انگلیسی'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='پیش‌فرض سیستم',
        help_text='داده‌های پیش‌فرض قابل حذف نیستند'
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='افزوده شده توسط'
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد استفاده',
        help_text='برای مرتب‌سازی بر اساس محبوبیت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'patients_medical_term'
        verbose_name = 'اصطلاح پزشکی'
        verbose_name_plural = 'اصطلاحات پزشکی'
        ordering = ['-usage_count', 'name_fa']
        indexes = [
            models.Index(fields=['category', 'name_fa']),
            models.Index(fields=['category', 'name_en']),
            models.Index(fields=['category', '-usage_count']),
        ]
        # جلوگیری از تکرار نام در هر دسته
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name_fa'],
                name='unique_term_fa'
            ),
        ]
    
    def __str__(self):
        if self.name_en:
            return f"{self.name_fa} ({self.name_en})"
        return self.name_fa


class Allergy(models.Model):
    """
    مدل حساسیت‌های بیمار
    """
    
    SEVERITY_CHOICES = [
        ('mild', 'خفیف'),
        ('moderate', 'متوسط'),
        ('severe', 'شدید'),
    ]
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='allergies',
        verbose_name='بیمار'
    )
    allergen = models.CharField(
        max_length=100,
        verbose_name='عامل حساسیت'
    )
    reaction = models.TextField(
        blank=True,
        null=True,
        verbose_name='واکنش'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='moderate',
        verbose_name='شدت'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='یادداشت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )
    
    class Meta:
        db_table = 'patients_allergy'
        verbose_name = 'حساسیت'
        verbose_name_plural = 'حساسیت‌ها'
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.allergen}"


class PrescriptionItem(models.Model):
    """
    مدل آیتم‌های تجویز (دارو، آزمایش، تصویربرداری، اقدام درمانی)
    هر پرونده می‌تواند چند آیتم تجویز داشته باشد.
    """
    
    ITEM_TYPE_CHOICES = [
        ('medication', 'دارو'),
        ('lab_test', 'آزمایش'),
        ('imaging', 'تصویربرداری'),
        ('procedure', 'اقدام درمانی'),
    ]
    
    # فرم‌های دارویی
    FORM_CHOICES = [
        ('tablet', 'قرص'),
        ('capsule', 'کپسول'),
        ('syrup', 'شربت'),
        ('drop', 'قطره'),
        ('ointment', 'پماد'),
        ('cream', 'کرم'),
        ('injection', 'آمپول / تزریق'),
        ('suppository', 'شیاف'),
        ('inhaler', 'اسپری / استنشاقی'),
        ('spray', 'اسپری'),
        ('powder', 'پودر'),
        ('patch', 'چسب'),
        ('suspension', 'سوسپانسیون'),
        ('other', 'سایر'),
    ]
    
    # دوره مصرف
    FREQUENCY_CHOICES = [
        ('once_daily', 'روزی یک بار'),
        ('twice_daily', 'روزی دو بار'),
        ('three_daily', 'روزی سه بار'),
        ('four_daily', 'روزی چهار بار'),
        ('every_6h', 'هر ۶ ساعت'),
        ('every_8h', 'هر ۸ ساعت'),
        ('every_12h', 'هر ۱۲ ساعت'),
        ('weekly', 'هفته‌ای یک بار'),
        ('twice_weekly', 'هفته‌ای دو بار'),
        ('monthly', 'ماهی یک بار'),
        ('as_needed', 'در صورت نیاز'),
        ('once', 'فقط یک بار'),
        ('continuous', 'مداوم / همیشه'),
        ('custom', 'سفارشی'),
    ]
    
    # زمان مصرف
    TIMING_CHOICES = [
        ('before_meal', 'قبل از غذا'),
        ('after_meal', 'بعد از غذا'),
        ('with_meal', 'همراه غذا'),
        ('empty_stomach', 'ناشتا'),
        ('before_sleep', 'قبل از خواب'),
        ('morning', 'صبح'),
        ('noon', 'ظهر'),
        ('evening', 'عصر'),
        ('night', 'شب'),
        ('any', 'بدون محدودیت'),
    ]
    
    # واحد مدت
    DURATION_UNIT_CHOICES = [
        ('day', 'روز'),
        ('week', 'هفته'),
        ('month', 'ماه'),
        ('continuous', 'همیشه / مداوم'),
    ]
    
    # روابط
    record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescription_items',
        verbose_name='پرونده'
    )
    
    # نوع تجویز
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        default='medication',
        verbose_name='نوع تجویز'
    )
    
    # نام آیتم
    name = models.CharField(
        max_length=200,
        verbose_name='نام'
    )
    name_en = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='نام انگلیسی'
    )
    
    # فرم دارو (فقط برای دارو)
    form = models.CharField(
        max_length=20,
        choices=FORM_CHOICES,
        blank=True,
        null=True,
        verbose_name='فرم دارو'
    )
    
    # دوز / تعداد
    dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='دوز / مقدار',
        help_text='مثلاً: ۱ عدد، ۵ سی‌سی، ۵۰۰ میلی‌گرم'
    )
    
    # دوره مصرف
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        blank=True,
        null=True,
        verbose_name='دوره مصرف'
    )
    frequency_custom = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='دوره سفارشی',
        help_text='اگر دوره سفارشی انتخاب شود'
    )
    
    # زمان مصرف
    timing = models.CharField(
        max_length=20,
        choices=TIMING_CHOICES,
        blank=True,
        null=True,
        verbose_name='زمان مصرف'
    )
    
    # مدت مصرف
    duration_value = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='مدت'
    )
    duration_unit = models.CharField(
        max_length=20,
        choices=DURATION_UNIT_CHOICES,
        blank=True,
        null=True,
        verbose_name='واحد مدت'
    )
    
    # تعداد (برای دارو: تعداد کل توزیع)
    quantity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='تعداد کل',
        help_text='تعداد کل اقلام (مثلاً: ۲۰ عدد، ۱ بسته)'
    )
    
    # دستور خاص
    instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name='دستور / توضیحات'
    )
    
    # ترتیب
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        db_table = 'patients_prescription_item'
        verbose_name = 'آیتم تجویز'
        verbose_name_plural = 'آیتم‌های تجویز'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['record', 'item_type']),
        ]
    
    def __str__(self):
        return f"{self.get_item_type_display()}: {self.name}"
    
    def get_full_description(self):
        """توضیح کامل تجویز"""
        parts = [self.name]
        if self.form:
            parts.append(self.get_form_display())
        if self.dosage:
            parts.append(self.dosage)
        if self.frequency:
            if self.frequency == 'custom' and self.frequency_custom:
                parts.append(self.frequency_custom)
            else:
                parts.append(self.get_frequency_display())
        if self.timing:
            parts.append(self.get_timing_display())
        if self.duration_value and self.duration_unit:
            if self.duration_unit == 'continuous':
                parts.append('مداوم')
            else:
                parts.append(f'{self.duration_value} {self.get_duration_unit_display()}')
        return ' • '.join(parts)

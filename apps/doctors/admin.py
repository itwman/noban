"""
پنل ادمین اپلیکیشن پزشکان - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Doctor, DoctorClinic, WorkSchedule, DoctorHoliday, Specialization,
    ServiceType, InsuranceType, DoctorTariff
)


class DoctorClinicInline(admin.TabularInline):
    """نمایش مراکز پزشک"""
    model = DoctorClinic
    extra = 1
    fields = ('clinic', 'is_primary', 'room_number', 'custom_visit_fee', 'is_active')


class WorkScheduleInline(admin.TabularInline):
    """نمایش تقویم کاری"""
    model = WorkSchedule
    extra = 1
    fields = ('clinic', 'day_of_week', 'start_time', 'end_time', 'is_active')


class DoctorHolidayInline(admin.TabularInline):
    """نمایش تعطیلات"""
    model = DoctorHoliday
    extra = 1
    fields = ('date', 'clinic', 'holiday_type', 'reason')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """پنل ادمین پزشکان"""
    
    list_display = (
        'get_full_name', 'specialization', 'medical_code',
        'visit_fee', 'is_active', 'is_featured', 'profile_preview'
    )
    list_filter = ('is_active', 'is_featured', 'specialization', 'allows_online_booking')
    search_fields = (
        'user__first_name', 'user__last_name', 'user__phone',
        'medical_code', 'specialization'
    )
    ordering = ('user__last_name',)
    readonly_fields = ('created_at', 'updated_at', 'profile_preview')
    raw_id_fields = ('user',)
    inlines = [DoctorClinicInline, WorkScheduleInline, DoctorHolidayInline]
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('اطلاعات حرفه‌ای', {
            'fields': (
                'specialization', 'medical_code', 'bio',
                'education', 'experience_years', 'profile_image', 'profile_preview'
            )
        }),
        ('تنظیمات نوبت‌دهی', {
            'fields': (
                'visit_duration', 'gap_between_visits', 'max_daily_appointments',
                'max_advance_days', 'min_cancel_hours'
            )
        }),
        ('تنظیمات مالی', {
            'fields': ('visit_fee', 'deposit_percent')
        }),
        ('وضعیت', {
            'fields': ('is_active', 'is_featured', 'allows_online_booking', 'requires_payment')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_title()
    get_full_name.short_description = 'نام پزشک'
    get_full_name.admin_order_field = 'user__last_name'
    
    def profile_preview(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return '-'
    profile_preview.short_description = 'تصویر'


@admin.register(DoctorClinic)
class DoctorClinicAdmin(admin.ModelAdmin):
    """پنل ادمین ارتباط پزشک-مرکز"""
    
    list_display = ('doctor', 'clinic', 'is_primary', 'room_number', 'is_active', 'get_visit_fee')
    list_filter = ('is_active', 'is_primary', 'clinic')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    raw_id_fields = ('doctor', 'clinic')
    
    def get_visit_fee(self, obj):
        return f"{obj.get_visit_fee():,} تومان"
    get_visit_fee.short_description = 'هزینه ویزیت'


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    """پنل ادمین تقویم کاری"""
    
    list_display = ('doctor', 'clinic', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'clinic')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    ordering = ('doctor', 'day_of_week', 'start_time')
    raw_id_fields = ('doctor', 'clinic')


@admin.register(DoctorHoliday)
class DoctorHolidayAdmin(admin.ModelAdmin):
    """پنل ادمین تعطیلات"""
    
    list_display = ('doctor', 'date', 'clinic', 'holiday_type', 'reason')
    list_filter = ('holiday_type', 'date', 'clinic')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'reason')
    ordering = ('-date',)
    date_hierarchy = 'date'
    raw_id_fields = ('doctor', 'clinic')


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    """پنل ادمین تخصص‌ها"""
    
    list_display = ('name', 'name_en', 'icon', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'name_en')
    ordering = ('order', 'name')
    list_editable = ('order', 'is_active')


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    """پنل ادمین انواع خدمات پزشکی"""
    
    list_display = ('name', 'slug', 'icon', 'is_default', 'is_active', 'sort_order')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'slug', 'description')
    ordering = ('sort_order', 'name')
    list_editable = ('sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        """خدمات پیش‌فرض سیستم قابل حذف نیستند"""
        if obj and obj.is_default:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(InsuranceType)
class InsuranceTypeAdmin(admin.ModelAdmin):
    """پنل ادمین انواع بیمه"""
    
    list_display = ('name', 'slug', 'icon', 'is_default', 'is_active', 'sort_order')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'slug', 'description')
    ordering = ('sort_order', 'name')
    list_editable = ('sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        """بیمه‌های پیش‌فرض سیستم قابل حذف نیستند"""
        if obj and obj.is_default:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(DoctorTariff)
class DoctorTariffAdmin(admin.ModelAdmin):
    """پنل ادمین تعرفه‌های پزشک"""
    
    list_display = (
        'doctor', 'clinic_display', 'service_type', 'insurance_type',
        'fee_display', 'deposit_display', 'online_payment_required', 'is_active'
    )
    list_filter = ('is_active', 'service_type', 'insurance_type', 'deposit_required', 'online_payment_required')
    search_fields = (
        'doctor__user__first_name', 'doctor__user__last_name',
        'clinic__name', 'service_type__name', 'insurance_type__name'
    )
    raw_id_fields = ('doctor', 'clinic')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('ارتباطات', {
            'fields': ('doctor', 'clinic', 'service_type', 'insurance_type')
        }),
        ('مبلغ تعرفه', {
            'fields': ('fee',)
        }),
        ('تنظیمات بیعانه', {
            'fields': ('deposit_required', 'deposit_amount', 'deposit_percent'),
            'description': 'اگر مبلغ بیعانه صفر باشد، از درصد بیعانه استفاده می‌شود'
        }),
        ('تنظیمات پرداخت', {
            'fields': ('online_payment_required',)
        }),
        ('سایر', {
            'fields': ('description', 'is_active', 'created_at', 'updated_at')
        }),
    )
    
    def clinic_display(self, obj):
        return obj.clinic.name if obj.clinic else 'همه مراکز (عمومی)'
    clinic_display.short_description = 'مرکز'
    
    def fee_display(self, obj):
        return f"{obj.fee:,.0f} ریال"
    fee_display.short_description = 'مبلغ تعرفه'
    fee_display.admin_order_field = 'fee'
    
    def deposit_display(self, obj):
        amount = obj.get_deposit_amount()
        if amount > 0:
            return f"{amount:,.0f} ریال"
        return '-'
    deposit_display.short_description = 'بیعانه'

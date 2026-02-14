"""
پنل ادمین اپلیکیشن مراکز پزشکی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Clinic, ClinicImage


class ClinicImageInline(admin.TabularInline):
    """
    نمایش تصاویر مرکز به صورت Inline
    """
    model = ClinicImage
    extra = 1
    fields = ('image', 'title', 'is_primary', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'پیش‌نمایش'


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    """
    پنل ادمین مراکز پزشکی
    """
    
    list_display = (
        'name', 'city', 'province', 'phone', 
        'is_active', 'allows_online_booking', 'logo_preview'
    )
    list_filter = ('province', 'city', 'is_active', 'allows_online_booking', 'requires_payment')
    search_fields = ('name', 'phone', 'address', 'license_number')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    inlines = [ClinicImageInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'phone', 'mobile', 'email', 'logo', 'logo_preview')
        }),
        ('نشانی', {
            'fields': ('province', 'city', 'address', 'postal_code', 'latitude', 'longitude')
        }),
        ('اطلاعات تکمیلی', {
            'fields': ('description', 'license_number'),
            'classes': ('collapse',)
        }),
        ('تنظیمات', {
            'fields': ('is_active', 'allows_online_booking', 'requires_payment')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        """پیش‌نمایش لوگو"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: contain;" />',
                obj.logo.url
            )
        return '-'
    logo_preview.short_description = 'لوگو'


@admin.register(ClinicImage)
class ClinicImageAdmin(admin.ModelAdmin):
    """
    پنل ادمین تصاویر مراکز
    """
    
    list_display = ('clinic', 'title', 'is_primary', 'order', 'image_preview', 'created_at')
    list_filter = ('clinic', 'is_primary', 'created_at')
    search_fields = ('clinic__name', 'title')
    ordering = ('clinic', 'order')
    readonly_fields = ('created_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'پیش‌نمایش'

"""
پنل ادمین اپلیکیشن صف زنده - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import QueueStatus, QueueLog, QueueAnnouncement


@admin.register(QueueStatus)
class QueueStatusAdmin(admin.ModelAdmin):
    """پنل ادمین وضعیت صف"""
    
    list_display = (
        'doctor_name', 'clinic', 'date', 'current_queue_number',
        'completed_appointments', 'remaining_appointments',
        'is_doctor_available', 'last_update'
    )
    list_filter = ('date', 'clinic', 'is_doctor_available')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    ordering = ('-date',)
    date_hierarchy = 'date'
    readonly_fields = ('last_update',)
    raw_id_fields = ('doctor', 'clinic', 'current_appointment')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('doctor', 'clinic', 'date')
        }),
        ('وضعیت فعلی', {
            'fields': ('current_queue_number', 'current_appointment')
        }),
        ('آمار', {
            'fields': (
                'total_appointments', 'completed_appointments',
                'remaining_appointments', 'average_visit_duration',
                'estimated_wait_time'
            )
        }),
        ('وضعیت پزشک', {
            'fields': ('is_doctor_available', 'doctor_break_until')
        }),
        ('تاریخ‌ها', {
            'fields': ('started_at', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_title()
    doctor_name.short_description = 'پزشک'


@admin.register(QueueLog)
class QueueLogAdmin(admin.ModelAdmin):
    """پنل ادمین لاگ صف"""
    
    list_display = ('queue_status', 'action', 'appointment', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = (
        'queue_status__doctor__user__first_name',
        'queue_status__doctor__user__last_name'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('queue_status', 'appointment', 'performed_by')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(QueueAnnouncement)
class QueueAnnouncementAdmin(admin.ModelAdmin):
    """پنل ادمین اعلان‌های صف"""
    
    list_display = (
        'message_preview', 'doctor', 'clinic', 'is_global',
        'is_active', 'priority', 'start_date', 'end_date'
    )
    list_filter = ('is_global', 'is_active', 'clinic')
    search_fields = ('message',)
    ordering = ('-priority', '-created_at')
    list_editable = ('is_active', 'priority')
    raw_id_fields = ('doctor', 'clinic')
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'پیام'

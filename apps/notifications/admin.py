"""
پنل ادمین اپلیکیشن اعلان‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SMS, SMSTemplate, SMSSetting, Notification


@admin.register(SMS)
class SMSAdmin(admin.ModelAdmin):
    """پنل ادمین پیامک‌ها"""
    
    list_display = (
        'receptor', 'template', 'status_badge', 'message_preview',
        'cost', 'created_at', 'sent_at'
    )
    list_filter = ('status', 'template', 'created_at')
    search_fields = ('receptor', 'message', 'message_id')
    ordering = ('-created_at',)
    readonly_fields = (
        'message_id', 'cost', 'error_code', 'error_message',
        'created_at', 'sent_at', 'delivered_at'
    )
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('receptor', 'message', 'template')
        }),
        ('وضعیت', {
            'fields': ('status', 'message_id', 'cost')
        }),
        ('خطا', {
            'fields': ('error_code', 'error_message'),
            'classes': ('collapse',)
        }),
        ('ارتباط', {
            'fields': ('related_model', 'related_id'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'sent_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'پیام'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'sent': '#17a2b8',
            'delivered': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    """پنل ادمین الگوهای پیامک"""
    
    list_display = ('name', 'title', 'is_active', 'content_preview', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'title', 'content')
    ordering = ('name',)
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'محتوا'


@admin.register(SMSSetting)
class SMSSettingAdmin(admin.ModelAdmin):
    """پنل ادمین تنظیمات پیامک"""
    
    list_display = (
        'is_active', 'line_number', 'send_appointment_confirm',
        'send_appointment_reminder', 'updated_at'
    )
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('اطلاعات سرویس', {
            'fields': ('api_key', 'line_number', 'is_active')
        }),
        ('تنظیمات ارسال', {
            'fields': (
                'send_appointment_confirm', 'send_appointment_reminder',
                'reminder_hours_before', 'send_queue_update',
                'send_cancel_notification', 'max_daily_sms'
            )
        }),
        ('اطلاعات', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not SMSSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """پنل ادمین اعلان‌ها"""
    
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__phone', 'user__first_name', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'read_at')
    raw_id_fields = ('user',)
    
    actions = ['mark_as_read']
    
    @admin.action(description='علامت‌گذاری به عنوان خوانده شده')
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        self.message_user(request, f'{count} اعلان خوانده شد.')

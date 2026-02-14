"""
پنل ادمین اپلیکیشن کاربران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, VerificationCode, UserSession, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    پنل ادمین کاربران
    """
    
    list_display = (
        'phone', 'get_full_name', 'role', 'is_active', 
        'is_verified', 'date_joined', 'profile_image_preview'
    )
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff', 'gender', 'date_joined')
    search_fields = ('phone', 'first_name', 'last_name', 'national_code', 'email')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'profile_image_preview')
    
    fieldsets = (
        ('اطلاعات ورود', {
            'fields': ('phone', 'password')
        }),
        ('اطلاعات شخصی', {
            'fields': (
                'first_name', 'last_name', 'email', 'national_code',
                'birth_date', 'gender', 'address', 'profile_image', 'profile_image_preview'
            )
        }),
        ('نقش و دسترسی', {
            'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('تاریخ‌ها', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('اطلاعات اولیه', {
            'classes': ('wide',),
            'fields': (
                'phone', 'password1', 'password2', 'first_name', 'last_name',
                'role', 'is_active', 'is_staff'
            ),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    def profile_image_preview(self, obj):
        """پیش‌نمایش تصویر پروفایل"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return '-'
    profile_image_preview.short_description = 'تصویر'


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """
    پنل ادمین کدهای تأیید
    """
    
    list_display = ('phone', 'code', 'code_type', 'is_used', 'created_at', 'expires_at', 'status_badge')
    list_filter = ('code_type', 'is_used', 'created_at')
    search_fields = ('phone', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def status_badge(self, obj):
        """نمایش وضعیت با رنگ"""
        if obj.is_used:
            return format_html('<span style="color: red;">استفاده شده</span>')
        elif obj.is_valid():
            return format_html('<span style="color: green;">معتبر</span>')
        else:
            return format_html('<span style="color: orange;">منقضی</span>')
    status_badge.short_description = 'وضعیت'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    پنل ادمین نشست‌های کاربران
    """
    
    list_display = (
        'user', 'device_type', 'browser', 'os', 
        'ip_address', 'location', 'is_active', 'last_activity'
    )
    list_filter = ('is_active', 'device_type', 'browser', 'os', 'created_at')
    search_fields = ('user__phone', 'user__first_name', 'user__last_name', 'ip_address')
    ordering = ('-last_activity',)
    readonly_fields = ('session_key', 'user_agent', 'created_at', 'last_activity')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('اطلاعات دستگاه', {
            'fields': ('device_type', 'browser', 'os', 'user_agent')
        }),
        ('اطلاعات شبکه', {
            'fields': ('ip_address', 'location')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['terminate_sessions']
    
    @admin.action(description='خاتمه دادن نشست‌های انتخاب شده')
    def terminate_sessions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} نشست خاتمه یافت.')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    پنل ادمین لاگ تغییرات
    """
    
    list_display = ('user', 'action', 'model_name', 'object_repr', 'ip_address', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__phone', 'model_name', 'object_repr', 'ip_address')
    ordering = ('-created_at',)
    readonly_fields = (
        'user', 'action', 'model_name', 'object_id', 'object_repr',
        'changes', 'ip_address', 'user_agent', 'created_at'
    )
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('اطلاعات عملیات', {
            'fields': ('action', 'model_name', 'object_id', 'object_repr')
        }),
        ('تغییرات', {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        ('تاریخ', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

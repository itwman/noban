"""
پنل ادمین اپلیکیشن پرداخت - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, Refund, PaymentSetting


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """پنل ادمین تراکنش‌ها"""
    
    list_display = (
        'uuid_short', 'user_name', 'appointment_info', 'amount_display',
        'gateway', 'transaction_type', 'status_badge', 'created_at'
    )
    list_filter = ('status', 'gateway', 'transaction_type', 'created_at')
    search_fields = (
        'uuid', 'user__phone', 'user__first_name', 'user__last_name',
        'ref_id', 'authority'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = (
        'uuid', 'created_at', 'paid_at', 'verified_at',
        'callback_data', 'ip_address', 'user_agent'
    )
    raw_id_fields = ('appointment', 'user')
    
    fieldsets = (
        ('شناسه', {
            'fields': ('uuid',)
        }),
        ('اطلاعات اصلی', {
            'fields': ('appointment', 'user', 'amount', 'gateway', 'transaction_type')
        }),
        ('اطلاعات درگاه', {
            'fields': ('authority', 'ref_id', 'card_number', 'card_hash')
        }),
        ('وضعیت', {
            'fields': ('status', 'description', 'error_code', 'error_message')
        }),
        ('اطلاعات فنی', {
            'fields': ('ip_address', 'user_agent', 'callback_data'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'paid_at', 'verified_at'),
            'classes': ('collapse',)
        }),
    )
    
    def uuid_short(self, obj):
        return str(obj.uuid)[:8] + '...'
    uuid_short.short_description = 'شناسه'
    
    def user_name(self, obj):
        return obj.user.get_full_name()
    user_name.short_description = 'کاربر'
    
    def appointment_info(self, obj):
        return f"نوبت #{obj.appointment.id}"
    appointment_info.short_description = 'نوبت'
    
    def amount_display(self, obj):
        return f"{obj.amount:,.0f} تومان"
    amount_display.short_description = 'مبلغ'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'paid': '#28a745',
            'verified': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
            'refunded': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'
    
    actions = ['verify_transactions']
    
    @admin.action(description='تأیید تراکنش‌های انتخاب شده')
    def verify_transactions(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(status='paid').update(
            status='verified',
            verified_at=timezone.now()
        )
        self.message_user(request, f'{count} تراکنش تأیید شد.')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """پنل ادمین بازپرداخت‌ها"""
    
    list_display = (
        'transaction', 'amount_display', 'reason', 'status_badge',
        'processed_by', 'created_at'
    )
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('transaction__uuid', 'transaction__user__phone', 'ref_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'processed_at')
    raw_id_fields = ('transaction', 'processed_by')
    
    def amount_display(self, obj):
        return f"{obj.amount:,.0f} تومان"
    amount_display.short_description = 'مبلغ'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'rejected': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'


@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    """پنل ادمین تنظیمات پرداخت"""
    
    list_display = (
        'default_gateway', 'zarinpal_active', 'drik_active',
        'allow_deposit', 'allow_cash', 'updated_at'
    )
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('زرین‌پال', {
            'fields': ('zarinpal_merchant_id', 'zarinpal_sandbox', 'zarinpal_active')
        }),
        ('دریک', {
            'fields': ('drik_api_key', 'drik_sandbox', 'drik_active')
        }),
        ('تنظیمات عمومی', {
            'fields': ('default_gateway', 'min_payment_amount', 'allow_deposit', 'allow_cash')
        }),
        ('اطلاعات', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # فقط یک رکورد تنظیمات مجاز است
        return not PaymentSetting.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

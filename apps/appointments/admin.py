"""
پنل ادمین اپلیکیشن نوبت‌دهی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment, AppointmentHistory, TimeSlot


class AppointmentHistoryInline(admin.TabularInline):
    """نمایش تاریخچه تغییرات"""
    model = AppointmentHistory
    extra = 0
    readonly_fields = ('changed_by', 'field_name', 'old_value', 'new_value', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """پنل ادمین نوبت‌ها"""
    
    list_display = (
        'id', 'patient_name', 'doctor_name', 'clinic',
        'date', 'time', 'queue_number', 'status_badge', 
        'payment_status_badge', 'booking_source'
    )
    list_filter = (
        'status', 'payment_status', 'booking_source',
        'date', 'clinic', 'doctor', 'service_type', 'insurance_type'
    )
    search_fields = (
        'patient__first_name', 'patient__last_name', 'patient__phone',
        'doctor__user__first_name', 'doctor__user__last_name',
        'clinic__name'
    )
    ordering = ('-date', 'time')
    date_hierarchy = 'date'
    readonly_fields = (
        'created_at', 'updated_at', 'arrived_at', 'visit_started_at',
        'visited_at', 'cancelled_at'
    )
    raw_id_fields = ('patient', 'doctor', 'clinic', 'created_by', 'cancelled_by', 'tariff')
    inlines = [AppointmentHistoryInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('patient', 'doctor', 'clinic')
        }),
        ('تعرفه', {
            'fields': ('service_type', 'insurance_type', 'tariff', 'tariff_fee'),
            'classes': ('collapse',)
        }),
        ('زمان نوبت', {
            'fields': ('date', 'time', 'queue_number', 'estimated_time')
        }),
        ('وضعیت', {
            'fields': ('status', 'booking_source')
        }),
        ('پرداخت', {
            'fields': (
                'payment_status', 'payment_type', 'payment_amount',
                'deposit_amount', 'paid_amount'
            )
        }),
        ('یادداشت‌ها', {
            'fields': ('patient_notes', 'secretary_notes', 'doctor_notes'),
            'classes': ('collapse',)
        }),
        ('لغو', {
            'fields': ('cancelled_at', 'cancelled_by', 'cancel_reason'),
            'classes': ('collapse',)
        }),
        ('اعلان‌ها', {
            'fields': ('reminder_sent', 'confirm_sms_sent'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': (
                'created_by', 'created_at', 'updated_at',
                'arrived_at', 'visit_started_at', 'visited_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'بیمار'
    patient_name.admin_order_field = 'patient__last_name'
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_title()
    doctor_name.short_description = 'پزشک'
    doctor_name.admin_order_field = 'doctor__user__last_name'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'arrived': '#007bff',
            'in_progress': '#6f42c1',
            'visited': '#28a745',
            'cancelled': '#dc3545',
            'no_show': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'وضعیت'
    
    def payment_status_badge(self, obj):
        colors = {
            'unpaid': '#dc3545',
            'deposit': '#ffc107',
            'paid': '#28a745',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'پرداخت'
    
    actions = ['confirm_appointments', 'cancel_appointments', 'mark_as_visited']
    
    @admin.action(description='تأیید نوبت‌های انتخاب شده')
    def confirm_appointments(self, request, queryset):
        count = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{count} نوبت تأیید شد.')
    
    @admin.action(description='لغو نوبت‌های انتخاب شده')
    def cancel_appointments(self, request, queryset):
        from django.utils import timezone
        count = queryset.exclude(status__in=['cancelled', 'visited']).update(
            status='cancelled',
            cancelled_at=timezone.now(),
            cancelled_by=request.user
        )
        self.message_user(request, f'{count} نوبت لغو شد.')
    
    @admin.action(description='علامت‌گذاری به عنوان ویزیت شده')
    def mark_as_visited(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(status__in=['confirmed', 'arrived', 'in_progress']).update(
            status='visited',
            visited_at=timezone.now()
        )
        self.message_user(request, f'{count} نوبت ویزیت شد.')


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    """پنل ادمین تاریخچه نوبت‌ها"""
    
    list_display = ('appointment', 'changed_by', 'field_name', 'old_value', 'new_value', 'created_at')
    list_filter = ('field_name', 'created_at')
    search_fields = ('appointment__patient__phone', 'appointment__id')
    ordering = ('-created_at',)
    readonly_fields = ('appointment', 'changed_by', 'field_name', 'old_value', 'new_value', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """پنل ادمین تایم‌ها"""
    
    list_display = ('doctor', 'clinic', 'date', 'time', 'is_available', 'is_blocked')
    list_filter = ('is_available', 'is_blocked', 'date', 'clinic')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    ordering = ('-date', 'time')
    date_hierarchy = 'date'
    raw_id_fields = ('doctor', 'clinic')

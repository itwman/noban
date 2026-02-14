"""
پنل ادمین اپلیکیشن گزارش‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import DailyReport, MonthlyReport, FinancialSummary, ExportedReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    """پنل ادمین گزارش روزانه"""
    
    list_display = (
        'date', 'doctor_name', 'clinic', 'total_appointments',
        'completed_appointments', 'cancelled_appointments',
        'revenue_display', 'completion_rate'
    )
    list_filter = ('date', 'clinic', 'doctor')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    ordering = ('-date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('doctor', 'clinic')
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('doctor', 'clinic', 'date')
        }),
        ('آمار نوبت‌ها', {
            'fields': (
                'total_appointments', 'completed_appointments',
                'cancelled_appointments', 'no_show_appointments', 'new_patients'
            )
        }),
        ('آمار مالی', {
            'fields': ('total_revenue', 'online_revenue', 'cash_revenue', 'refunded_amount')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_title() if obj.doctor else '-'
    doctor_name.short_description = 'پزشک'
    
    def revenue_display(self, obj):
        return f"{obj.total_revenue:,.0f} تومان"
    revenue_display.short_description = 'درآمد'
    
    def completion_rate(self, obj):
        rate = obj.get_completion_rate()
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 50 else '#dc3545'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    completion_rate.short_description = 'نرخ تکمیل'


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    """پنل ادمین گزارش ماهانه"""
    
    list_display = (
        'year', 'month', 'doctor_name', 'clinic',
        'total_appointments', 'unique_patients', 'revenue_display'
    )
    list_filter = ('year', 'month', 'clinic', 'doctor')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name', 'clinic__name')
    ordering = ('-year', '-month')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('doctor', 'clinic')
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_title() if obj.doctor else '-'
    doctor_name.short_description = 'پزشک'
    
    def revenue_display(self, obj):
        return f"{obj.total_revenue:,.0f} تومان"
    revenue_display.short_description = 'درآمد'


@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    """پنل ادمین خلاصه مالی"""
    
    list_display = (
        'period_type', 'start_date', 'end_date', 'doctor', 'clinic',
        'income_display', 'net_display', 'transaction_count'
    )
    list_filter = ('period_type', 'clinic')
    ordering = ('-start_date',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('doctor', 'clinic')
    
    def income_display(self, obj):
        return f"{obj.total_income:,.0f}"
    income_display.short_description = 'درآمد'
    
    def net_display(self, obj):
        return f"{obj.net_income:,.0f}"
    net_display.short_description = 'خالص'


@admin.register(ExportedReport)
class ExportedReportAdmin(admin.ModelAdmin):
    """پنل ادمین گزارش‌های خروجی"""
    
    list_display = (
        'user', 'report_type', 'file_format', 'rows_count',
        'file_size_display', 'created_at', 'download_link'
    )
    list_filter = ('report_type', 'file_format', 'created_at')
    search_fields = ('user__phone', 'user__first_name')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'created_at')
    raw_id_fields = ('user',)
    
    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'حجم'
    
    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" download>دانلود</a>', obj.file.url)
        return '-'
    download_link.short_description = 'دانلود'

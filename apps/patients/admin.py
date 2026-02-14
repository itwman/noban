"""
پنل ادمین اپلیکیشن بیماران - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import MedicalRecord, MedicalFile, PatientNote, Allergy


class MedicalFileInline(admin.TabularInline):
    """نمایش فایل‌های پزشکی"""
    model = MedicalFile
    extra = 1
    fields = ('file', 'file_type', 'title', 'description')
    readonly_fields = ('file_size', 'created_at')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """پنل ادمین پرونده پزشکی"""
    
    list_display = (
        'patient_name', 'doctor_name', 'visit_date',
        'diagnosis_preview', 'files_count', 'created_at'
    )
    list_filter = ('visit_date', 'doctor', 'created_at')
    search_fields = (
        'patient__first_name', 'patient__last_name', 'patient__phone',
        'doctor__user__first_name', 'doctor__user__last_name',
        'diagnosis', 'prescription'
    )
    ordering = ('-visit_date',)
    date_hierarchy = 'visit_date'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient', 'doctor', 'appointment')
    inlines = [MedicalFileInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('patient', 'doctor', 'appointment', 'visit_date')
        }),
        ('شکایت و معاینه', {
            'fields': ('chief_complaint', 'history_of_present_illness', 'physical_examination')
        }),
        ('تشخیص و درمان', {
            'fields': ('diagnosis', 'prescription', 'notes')
        }),
        ('علائم حیاتی', {
            'fields': ('blood_pressure', 'pulse_rate', 'temperature', 'weight', 'height'),
            'classes': ('collapse',)
        }),
        ('پیگیری', {
            'fields': ('next_visit_date', 'follow_up_notes'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'بیمار'
    
    def doctor_name(self, obj):
        return obj.doctor.get_full_title()
    doctor_name.short_description = 'پزشک'
    
    def diagnosis_preview(self, obj):
        if obj.diagnosis:
            return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis
        return '-'
    diagnosis_preview.short_description = 'تشخیص'
    
    def files_count(self, obj):
        count = obj.files.count()
        return format_html('<span class="badge bg-info">{}</span>', count)
    files_count.short_description = 'فایل‌ها'


@admin.register(MedicalFile)
class MedicalFileAdmin(admin.ModelAdmin):
    """پنل ادمین فایل‌های پزشکی"""
    
    list_display = (
        'record', 'file_type', 'title', 'file_size_display',
        'uploaded_by', 'created_at'
    )
    list_filter = ('file_type', 'created_at')
    search_fields = ('record__patient__phone', 'title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'created_at')
    raw_id_fields = ('record', 'uploaded_by')
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'حجم'


@admin.register(PatientNote)
class PatientNoteAdmin(admin.ModelAdmin):
    """پنل ادمین یادداشت‌های بیمار"""
    
    list_display = ('patient', 'title', 'created_by', 'is_important', 'is_private', 'created_at')
    list_filter = ('is_important', 'is_private', 'created_at')
    search_fields = ('patient__phone', 'patient__first_name', 'title', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient', 'created_by')


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    """پنل ادمین حساسیت‌ها"""
    
    list_display = ('patient', 'allergen', 'severity', 'reaction_preview', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('patient__phone', 'patient__first_name', 'allergen')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    raw_id_fields = ('patient',)
    
    def reaction_preview(self, obj):
        if obj.reaction:
            return obj.reaction[:30] + '...' if len(obj.reaction) > 30 else obj.reaction
        return '-'
    reaction_preview.short_description = 'واکنش'

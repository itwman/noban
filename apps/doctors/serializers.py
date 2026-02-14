"""
Serializers برای بخش پزشکان و تعرفه‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from rest_framework import serializers
from .models import (
    Doctor, DoctorClinic, WorkSchedule, DoctorHoliday,
    ServiceType, InsuranceType, DoctorTariff, Specialization
)


class ServiceTypeSerializer(serializers.ModelSerializer):
    """سریالایزر انواع خدمات پزشکی"""

    class Meta:
        model = ServiceType
        fields = [
            'id', 'name', 'slug', 'description',
            'icon', 'is_default', 'is_active', 'sort_order'
        ]
        read_only_fields = ['is_default']


class InsuranceTypeSerializer(serializers.ModelSerializer):
    """سریالایزر انواع بیمه"""

    class Meta:
        model = InsuranceType
        fields = [
            'id', 'name', 'slug', 'description',
            'icon', 'is_default', 'is_active', 'sort_order'
        ]
        read_only_fields = ['is_default']


class DoctorTariffSerializer(serializers.ModelSerializer):
    """سریالایزر تعرفه‌های پزشک"""

    service_type_name = serializers.CharField(
        source='service_type.name', read_only=True
    )
    insurance_type_name = serializers.CharField(
        source='insurance_type.name', read_only=True
    )
    clinic_name = serializers.SerializerMethodField()
    calculated_deposit = serializers.SerializerMethodField()
    fee_display = serializers.SerializerMethodField()

    class Meta:
        model = DoctorTariff
        fields = [
            'id', 'doctor', 'clinic', 'clinic_name',
            'service_type', 'service_type_name',
            'insurance_type', 'insurance_type_name',
            'fee', 'fee_display',
            'deposit_required', 'deposit_amount',
            'deposit_percent', 'calculated_deposit',
            'online_payment_required', 'description', 'is_active',
        ]
        read_only_fields = ['doctor']

    def get_clinic_name(self, obj):
        return obj.clinic.name if obj.clinic else 'همه مراکز'

    def get_calculated_deposit(self, obj):
        return obj.get_deposit_amount()

    def get_fee_display(self, obj):
        return f"{obj.fee:,.0f}"


class TariffCalculateSerializer(serializers.Serializer):
    """سریالایزر محاسبه تعرفه (برای فرآیند رزرو)"""

    service_type = serializers.IntegerField(required=True)
    insurance_type = serializers.IntegerField(required=True)
    clinic = serializers.IntegerField(required=False, allow_null=True)


class BulkTariffItemSerializer(serializers.Serializer):
    """سریالایزر هر آیتم در ایجاد دسته‌ای"""

    service_type_id = serializers.IntegerField()
    insurance_type_id = serializers.IntegerField()
    fee = serializers.DecimalField(max_digits=12, decimal_places=0)
    deposit_required = serializers.BooleanField(default=False)
    deposit_amount = serializers.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )
    deposit_percent = serializers.IntegerField(default=0)
    online_payment_required = serializers.BooleanField(default=False)


class BulkTariffSerializer(serializers.Serializer):
    """سریالایزر ایجاد/ویرایش دسته‌ای تعرفه‌ها"""

    clinic_id = serializers.IntegerField(required=False, allow_null=True)
    tariffs = BulkTariffItemSerializer(many=True)


class DoctorSerializer(serializers.ModelSerializer):
    """سریالایزر پزشک"""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'specialization', 'medical_code',
            'visit_duration', 'gap_between_visits',
            'max_daily_appointments', 'is_active'
        ]

    def get_full_name(self, obj):
        return obj.get_full_title()

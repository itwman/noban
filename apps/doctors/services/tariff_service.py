"""
سرویس مدیریت و محاسبه تعرفه‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django.db import models
from ..models import DoctorTariff, ServiceType, InsuranceType, Doctor


class TariffService:
    """
    سرویس مدیریت و محاسبه تعرفه‌ها
    """
    
    @staticmethod
    def get_tariff(doctor_id, service_type_id, insurance_type_id, clinic_id=None):
        """
        یافتن تعرفه مناسب با اولویت:
        1. تعرفه اختصاصی مرکز (clinic_id مشخص)
        2. تعرفه عمومی (clinic_id = NULL)
        
        Args:
            doctor_id (int): شناسه پزشک
            service_type_id (int): شناسه نوع خدمت
            insurance_type_id (int): شناسه نوع بیمه
            clinic_id (int, optional): شناسه مرکز
        
        Returns:
            DoctorTariff|None: تعرفه یافت شده یا None
        """
        # ابتدا تعرفه اختصاصی مرکز
        if clinic_id:
            tariff = DoctorTariff.objects.filter(
                doctor_id=doctor_id,
                clinic_id=clinic_id,
                service_type_id=service_type_id,
                insurance_type_id=insurance_type_id,
                is_active=True
            ).first()
            if tariff:
                return tariff
        
        # سپس تعرفه عمومی
        tariff = DoctorTariff.objects.filter(
            doctor_id=doctor_id,
            clinic_id__isnull=True,
            service_type_id=service_type_id,
            insurance_type_id=insurance_type_id,
            is_active=True
        ).first()
        
        return tariff
    
    @staticmethod
    def get_doctor_tariffs(doctor_id, clinic_id=None):
        """
        دریافت تمام تعرفه‌های یک پزشک
        
        Args:
            doctor_id (int): شناسه پزشک
            clinic_id (int, optional): شناسه مرکز (برای فیلتر کردن)
        
        Returns:
            QuerySet: تعرفه‌های پزشک
        """
        queryset = DoctorTariff.objects.filter(
            doctor_id=doctor_id,
            is_active=True
        ).select_related('service_type', 'insurance_type', 'clinic')
        
        if clinic_id:
            # تعرفه‌های اختصاصی مرکز + تعرفه‌های عمومی
            queryset = queryset.filter(
                models.Q(clinic_id=clinic_id) | models.Q(clinic_id__isnull=True)
            )
        
        return queryset.order_by('service_type__sort_order', 'insurance_type__sort_order')
    
    @staticmethod
    def get_doctor_services(doctor_id, clinic_id=None):
        """
        دریافت خدمات فعال یک پزشک (که تعرفه دارند)
        
        Args:
            doctor_id (int): شناسه پزشک
            clinic_id (int, optional): شناسه مرکز
        
        Returns:
            QuerySet: خدمات فعال
        """
        tariffs = TariffService.get_doctor_tariffs(doctor_id, clinic_id)
        service_ids = tariffs.values_list('service_type_id', flat=True).distinct()
        
        return ServiceType.objects.filter(
            id__in=service_ids,
            is_active=True
        ).order_by('sort_order', 'name')
    
    @staticmethod
    def get_doctor_insurances(doctor_id, service_type_id, clinic_id=None):
        """
        دریافت بیمه‌های فعال برای یک خدمت خاص پزشک
        
        Args:
            doctor_id (int): شناسه پزشک
            service_type_id (int): شناسه نوع خدمت
            clinic_id (int, optional): شناسه مرکز
        
        Returns:
            QuerySet: بیمه‌های فعال
        """
        filters = {
            'doctor_id': doctor_id,
            'service_type_id': service_type_id,
            'is_active': True,
        }
        
        if clinic_id:
            tariffs = DoctorTariff.objects.filter(
                models.Q(clinic_id=clinic_id) | models.Q(clinic_id__isnull=True),
                **filters
            )
        else:
            tariffs = DoctorTariff.objects.filter(**filters)
        
        insurance_ids = tariffs.values_list('insurance_type_id', flat=True).distinct()
        
        return InsuranceType.objects.filter(
            id__in=insurance_ids,
            is_active=True
        ).order_by('sort_order', 'name')
    
    @staticmethod
    def calculate_booking_fee(doctor_id, service_type_id, insurance_type_id, clinic_id=None):
        """
        محاسبه مبلغ برای رزرو نوبت
        
        Args:
            doctor_id (int): شناسه پزشک
            service_type_id (int): شناسه نوع خدمت
            insurance_type_id (int): شناسه نوع بیمه
            clinic_id (int, optional): شناسه مرکز
        
        Returns:
            dict: اطلاعات محاسبه شده
                {
                    'success': bool,
                    'tariff_id': int,
                    'fee': Decimal,
                    'deposit_required': bool,
                    'deposit_amount': int,
                    'online_payment_required': bool,
                    'service_name': str,
                    'insurance_name': str,
                    'clinic_name': str,
                    'message': str  # در صورت خطا
                }
        """
        tariff = TariffService.get_tariff(
            doctor_id, service_type_id, insurance_type_id, clinic_id
        )
        
        if not tariff:
            return {
                'success': False,
                'message': 'تعرفه‌ای برای این ترکیب یافت نشد'
            }
        
        clinic_name = 'همه مراکز'
        if tariff.clinic:
            clinic_name = tariff.clinic.name
        
        return {
            'success': True,
            'tariff_id': tariff.id,
            'fee': tariff.fee,
            'deposit_required': tariff.deposit_required,
            'deposit_amount': tariff.get_deposit_amount(),
            'online_payment_required': tariff.online_payment_required,
            'service_name': tariff.service_type.name,
            'insurance_name': tariff.insurance_type.name,
            'clinic_name': clinic_name,
        }
    
    @staticmethod
    def bulk_create_tariffs(doctor_id, tariffs_data):
        """
        ایجاد دسته‌ای تعرفه‌ها (برای ماتریس تنظیم دسته‌ای)
        
        Args:
            doctor_id (int): شناسه پزشک
            tariffs_data (list): لیست دیکشنری‌های تعرفه
                [
                    {
                        'clinic_id': int|None,
                        'service_type_id': int,
                        'insurance_type_id': int,
                        'fee': Decimal,
                        'deposit_required': bool,
                        'deposit_amount': Decimal,
                        'deposit_percent': int,
                        'online_payment_required': bool,
                        'description': str
                    },
                    ...
                ]
        
        Returns:
            tuple: (تعرفه‌های ایجاد شده, تعداد ایجاد شده, تعداد بروزرسانی شده)
        """
        created_count = 0
        updated_count = 0
        created_tariffs = []
        
        for data in tariffs_data:
            tariff, is_new = DoctorTariff.objects.update_or_create(
                doctor_id=doctor_id,
                clinic_id=data.get('clinic_id'),
                service_type_id=data['service_type_id'],
                insurance_type_id=data['insurance_type_id'],
                defaults={
                    'fee': data.get('fee', 0),
                    'deposit_required': data.get('deposit_required', False),
                    'deposit_amount': data.get('deposit_amount', 0),
                    'deposit_percent': data.get('deposit_percent', 0),
                    'online_payment_required': data.get('online_payment_required', False),
                    'description': data.get('description', ''),
                    'is_active': True,
                }
            )
            
            created_tariffs.append(tariff)
            
            if is_new:
                created_count += 1
            else:
                updated_count += 1
        
        return created_tariffs, created_count, updated_count
    
    @staticmethod
    def get_tariffs_grouped_by_clinic(doctor_id):
        """
        دریافت تعرفه‌های پزشک گروه‌بندی شده بر اساس مرکز
        
        Args:
            doctor_id (int): شناسه پزشک
        
        Returns:
            dict: تعرفه‌ها گروه‌بندی شده
                {
                    clinic_id|None: {
                        'clinic': Clinic|None,
                        'clinic_name': str,
                        'tariffs': [DoctorTariff, ...]
                    }
                }
        """
        tariffs = DoctorTariff.objects.filter(
            doctor_id=doctor_id
        ).select_related(
            'service_type', 'insurance_type', 'clinic'
        ).order_by('service_type__sort_order', 'insurance_type__sort_order')
        
        grouped = {}
        for tariff in tariffs:
            key = tariff.clinic_id  # None برای تعرفه عمومی
            
            if key not in grouped:
                grouped[key] = {
                    'clinic': tariff.clinic,
                    'clinic_name': tariff.clinic.name if tariff.clinic else 'تعرفه عمومی (همه مراکز)',
                    'tariffs': []
                }
            
            grouped[key]['tariffs'].append(tariff)
        
        # مرتب‌سازی: تعرفه عمومی در آخر
        sorted_grouped = {}
        for key in sorted(grouped.keys(), key=lambda k: (k is None, k or 0)):
            sorted_grouped[key] = grouped[key]
        
        return sorted_grouped

    @staticmethod
    def get_tariff_matrix(doctor_id, clinic_id=None):
        """
        دریافت ماتریس تعرفه‌ها برای نمایش در رابط کاربری
        
        Args:
            doctor_id (int): شناسه پزشک
            clinic_id (int, optional): شناسه مرکز
        
        Returns:
            dict: ماتریس تعرفه‌ها
                {
                    'services': [ServiceType, ...],
                    'insurances': [InsuranceType, ...],
                    'matrix': {
                        service_id: {
                            insurance_id: {
                                'tariff': DoctorTariff|None,
                                'fee': Decimal,
                                'deposit': int,
                                ...
                            }
                        }
                    }
                }
        """
        # دریافت خدمات فعال پزشک
        services = TariffService.get_doctor_services(doctor_id, clinic_id)
        
        # دریافت تمام بیمه‌های فعال
        insurances = InsuranceType.objects.filter(is_active=True).order_by('sort_order', 'name')
        
        # ساخت ماتریس
        matrix = {}
        for service in services:
            matrix[service.id] = {}
            for insurance in insurances:
                tariff = TariffService.get_tariff(
                    doctor_id, service.id, insurance.id, clinic_id
                )
                
                if tariff:
                    matrix[service.id][insurance.id] = {
                        'tariff': tariff,
                        'fee': tariff.fee,
                        'deposit_required': tariff.deposit_required,
                        'deposit_amount': tariff.get_deposit_amount(),
                        'online_payment_required': tariff.online_payment_required,
                    }
                else:
                    matrix[service.id][insurance.id] = {
                        'tariff': None,
                        'fee': 0,
                        'deposit_required': False,
                        'deposit_amount': 0,
                        'online_payment_required': False,
                    }
        
        return {
            'services': services,
            'insurances': insurances,
            'matrix': matrix,
        }
    
    @staticmethod
    def delete_tariff(tariff_id, user):
        """
        حذف تعرفه (با بررسی دسترسی)
        
        Args:
            tariff_id (int): شناسه تعرفه
            user: کاربر درخواست‌کننده
        
        Returns:
            dict: نتیجه عملیات
                {
                    'success': bool,
                    'message': str
                }
        """
        try:
            tariff = DoctorTariff.objects.get(id=tariff_id)
            
            # بررسی دسترسی (فقط پزشک خودش یا superadmin)
            if user.role == 'superadmin' or (user.role == 'doctor' and tariff.doctor.user == user):
                tariff.delete()
                return {
                    'success': True,
                    'message': 'تعرفه با موفقیت حذف شد'
                }
            else:
                return {
                    'success': False,
                    'message': 'شما اجازه حذف این تعرفه را ندارید'
                }
        
        except DoctorTariff.DoesNotExist:
            return {
                'success': False,
                'message': 'تعرفه یافت نشد'
            }
    
    @staticmethod
    def validate_tariff_data(data):
        """
        اعتبارسنجی داده‌های تعرفه
        
        Args:
            data (dict): داده‌های تعرفه
        
        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        
        # بررسی فیلدهای الزامی
        required_fields = ['service_type_id', 'insurance_type_id', 'fee']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f'فیلد {field} الزامی است')
        
        # بررسی مبلغ تعرفه
        if 'fee' in data:
            try:
                fee = float(data['fee'])
                if fee < 0:
                    errors.append('مبلغ تعرفه نمی‌تواند منفی باشد')
            except (ValueError, TypeError):
                errors.append('مبلغ تعرفه نامعتبر است')
        
        # بررسی بیعانه
        if data.get('deposit_required'):
            deposit_amount = data.get('deposit_amount', 0)
            deposit_percent = data.get('deposit_percent', 0)
            
            if deposit_amount == 0 and deposit_percent == 0:
                errors.append('در صورت نیاز به بیعانه، باید مبلغ یا درصد بیعانه مشخص شود')
            
            if deposit_percent < 0 or deposit_percent > 100:
                errors.append('درصد بیعانه باید بین 0 تا 100 باشد')
        
        return len(errors) == 0, errors

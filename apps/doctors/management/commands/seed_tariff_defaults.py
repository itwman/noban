"""
دستور مدیریتی برای ایجاد داده‌های پیش‌فرض خدمات و بیمه‌ها - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان

استفاده:
    python manage.py seed_tariff_defaults
"""

from django.core.management.base import BaseCommand
from apps.doctors.models import ServiceType, InsuranceType


class Command(BaseCommand):
    help = 'ایجاد داده‌های پیش‌فرض انواع خدمات و بیمه‌ها'

    def handle(self, *args, **options):
        self.stdout.write('شروع ایجاد داده‌های پیش‌فرض...')
        
        self._create_service_types()
        self._create_insurance_types()
        
        self.stdout.write(self.style.SUCCESS('داده‌های پیش‌فرض با موفقیت ایجاد شدند.'))

    def _create_service_types(self):
        """ایجاد انواع خدمات پیش‌فرض"""
        services = [
            {
                'name': 'ویزیت',
                'slug': 'visit',
                'description': 'مراجعه و معاینه پزشک',
                'icon': 'fa-stethoscope',
                'sort_order': 1,
            },
            {
                'name': 'سونوگرافی',
                'slug': 'sonography',
                'description': 'سونوگرافی و تصویربرداری',
                'icon': 'fa-image',
                'sort_order': 2,
            },
            {
                'name': 'آزمایشگاه',
                'slug': 'laboratory',
                'description': 'آزمایش‌های پزشکی',
                'icon': 'fa-flask',
                'sort_order': 3,
            },
            {
                'name': 'نوار قلب',
                'slug': 'ecg',
                'description': 'الکتروکاردیوگرام',
                'icon': 'fa-heartbeat',
                'sort_order': 4,
            },
            {
                'name': 'تزریقات',
                'slug': 'injection',
                'description': 'تزریق و سرم‌تراپی',
                'icon': 'fa-syringe',
                'sort_order': 5,
            },
            {
                'name': 'مشاوره',
                'slug': 'consultation',
                'description': 'مشاوره پزشکی',
                'icon': 'fa-comments',
                'sort_order': 6,
            },
            {
                'name': 'جراحی سرپایی',
                'slug': 'minor-surgery',
                'description': 'جراحی‌های سرپایی',
                'icon': 'fa-cut',
                'sort_order': 7,
            },
            {
                'name': 'فیزیوتراپی',
                'slug': 'physiotherapy',
                'description': 'فیزیوتراپی و توانبخشی',
                'icon': 'fa-walking',
                'sort_order': 8,
            },
        ]

        created_count = 0
        for service_data in services:
            obj, created = ServiceType.objects.update_or_create(
                slug=service_data['slug'],
                defaults={
                    'name': service_data['name'],
                    'description': service_data['description'],
                    'icon': service_data['icon'],
                    'is_default': True,
                    'is_active': True,
                    'sort_order': service_data['sort_order'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ خدمت ایجاد شد: {obj.name}')
            else:
                self.stdout.write(f'  ℹ️ خدمت موجود است: {obj.name}')

        self.stdout.write(f'انواع خدمات: {created_count} مورد جدید ایجاد شد.')

    def _create_insurance_types(self):
        """ایجاد انواع بیمه پیش‌فرض"""
        insurances = [
            {
                'name': 'آزاد (بدون بیمه)',
                'slug': 'free',
                'description': 'بدون پوشش بیمه‌ای',
                'icon': 'fa-user',
                'sort_order': 1,
            },
            {
                'name': 'تأمین اجتماعی',
                'slug': 'tamin',
                'description': 'بیمه تأمین اجتماعی',
                'icon': 'fa-shield-alt',
                'sort_order': 2,
            },
            {
                'name': 'خدمات درمانی',
                'slug': 'khadamat',
                'description': 'بیمه خدمات درمانی',
                'icon': 'fa-hospital',
                'sort_order': 3,
            },
            {
                'name': 'نیروهای مسلح',
                'slug': 'niroha',
                'description': 'بیمه نیروهای مسلح',
                'icon': 'fa-star',
                'sort_order': 4,
            },
            {
                'name': 'سلامت ایرانیان',
                'slug': 'salamat',
                'description': 'بیمه سلامت ایرانیان',
                'icon': 'fa-plus-circle',
                'sort_order': 5,
            },
            {
                'name': 'بیمه تکمیلی',
                'slug': 'takmili',
                'description': 'بیمه‌های تکمیلی',
                'icon': 'fa-plus-square',
                'sort_order': 6,
            },
            {
                'name': 'سایر',
                'slug': 'other',
                'description': 'سایر بیمه‌ها',
                'icon': 'fa-ellipsis-h',
                'sort_order': 7,
            },
        ]

        created_count = 0
        for insurance_data in insurances:
            obj, created = InsuranceType.objects.update_or_create(
                slug=insurance_data['slug'],
                defaults={
                    'name': insurance_data['name'],
                    'description': insurance_data['description'],
                    'icon': insurance_data['icon'],
                    'is_default': True,
                    'is_active': True,
                    'sort_order': insurance_data['sort_order'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ بیمه ایجاد شد: {obj.name}')
            else:
                self.stdout.write(f'  ℹ️ بیمه موجود است: {obj.name}')

        self.stdout.write(f'انواع بیمه: {created_count} مورد جدید ایجاد شد.')

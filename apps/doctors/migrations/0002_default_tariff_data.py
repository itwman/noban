# Generated migration for default service and insurance types

from django.db import migrations


def create_default_services(apps, schema_editor):
    """ایجاد انواع خدمات پیش‌فرض"""
    ServiceType = apps.get_model('doctors', 'ServiceType')
    
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
            'slug': 'minor_surgery',
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
    
    for service_data in services:
        ServiceType.objects.get_or_create(
            slug=service_data['slug'],
            defaults={
                **service_data,
                'is_default': True,
                'is_active': True,
            }
        )


def create_default_insurances(apps, schema_editor):
    """ایجاد انواع بیمه پیش‌فرض"""
    InsuranceType = apps.get_model('doctors', 'InsuranceType')
    
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
    
    for insurance_data in insurances:
        InsuranceType.objects.get_or_create(
            slug=insurance_data['slug'],
            defaults={
                **insurance_data,
                'is_default': True,
                'is_active': True,
            }
        )


def reverse_func(apps, schema_editor):
    """حذف داده‌های پیش‌فرض (در صورت بازگشت)"""
    ServiceType = apps.get_model('doctors', 'ServiceType')
    InsuranceType = apps.get_model('doctors', 'InsuranceType')
    
    ServiceType.objects.filter(is_default=True).delete()
    InsuranceType.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0001_initial'),  # جایگزین با آخرین migration موجود
    ]

    operations = [
        migrations.RunPython(create_default_services, reverse_func),
        migrations.RunPython(create_default_insurances, reverse_func),
    ]

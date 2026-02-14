"""
مایگریشن افزودن مدل MedicalTerm
اصطلاحات پزشکی (علائم، تشخیص‌ها، داروها) با قابلیت autocomplete
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[('symptom', 'علامت / شکایت'), ('diagnosis', 'تشخیص'), ('medication', 'دارو')],
                    db_index=True, max_length=20, verbose_name='دسته‌بندی'
                )),
                ('name_fa', models.CharField(max_length=200, verbose_name='نام فارسی')),
                ('name_en', models.CharField(blank=True, max_length=200, null=True, verbose_name='نام انگلیسی')),
                ('is_default', models.BooleanField(default=False, help_text='داده\u200cهای پیش\u200cفرض قابل حذف نیستند', verbose_name='پیش\u200cفرض سیستم')),
                ('usage_count', models.PositiveIntegerField(default=0, help_text='برای مرتب\u200cسازی بر اساس محبوبیت', verbose_name='تعداد استفاده')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('added_by', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL, verbose_name='افزوده شده توسط'
                )),
            ],
            options={
                'verbose_name': 'اصطلاح پزشکی',
                'verbose_name_plural': 'اصطلاحات پزشکی',
                'db_table': 'patients_medical_term',
                'ordering': ['-usage_count', 'name_fa'],
            },
        ),
        migrations.AddIndex(
            model_name='medicalterm',
            index=models.Index(fields=['category', 'name_fa'], name='patients_me_categor_fa_idx'),
        ),
        migrations.AddIndex(
            model_name='medicalterm',
            index=models.Index(fields=['category', 'name_en'], name='patients_me_categor_en_idx'),
        ),
        migrations.AddIndex(
            model_name='medicalterm',
            index=models.Index(fields=['category', '-usage_count'], name='patients_me_categor_usage_idx'),
        ),
        migrations.AddConstraint(
            model_name='medicalterm',
            constraint=models.UniqueConstraint(fields=('category', 'name_fa'), name='unique_term_fa'),
        ),
    ]

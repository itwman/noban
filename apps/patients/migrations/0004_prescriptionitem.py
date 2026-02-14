"""
مایگریشن ایجاد مدل PrescriptionItem و به‌روزرسانی MedicalTerm
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_seed_medical_terms'),
    ]

    operations = [
        # به‌روزرسانی CATEGORY_CHOICES در MedicalTerm (فقط تغییر choices - نیاز به migration ندارد ولی مستند می‌شود)
        migrations.AlterField(
            model_name='medicalterm',
            name='category',
            field=models.CharField(
                choices=[
                    ('symptom', 'علامت / شکایت'),
                    ('diagnosis', 'تشخیص'),
                    ('medication', 'دارو'),
                    ('lab_test', 'آزمایش'),
                    ('imaging', 'تصویربرداری'),
                    ('procedure', 'اقدام درمانی'),
                ],
                db_index=True,
                max_length=20,
                verbose_name='دسته‌بندی',
            ),
        ),
        
        # ایجاد جدول PrescriptionItem
        migrations.CreateModel(
            name='PrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(
                    choices=[
                        ('medication', 'دارو'),
                        ('lab_test', 'آزمایش'),
                        ('imaging', 'تصویربرداری'),
                        ('procedure', 'اقدام درمانی'),
                    ],
                    default='medication',
                    max_length=20,
                    verbose_name='نوع تجویز',
                )),
                ('name', models.CharField(max_length=200, verbose_name='نام')),
                ('name_en', models.CharField(blank=True, max_length=200, null=True, verbose_name='نام انگلیسی')),
                ('form', models.CharField(
                    blank=True,
                    choices=[
                        ('tablet', 'قرص'), ('capsule', 'کپسول'), ('syrup', 'شربت'),
                        ('drop', 'قطره'), ('ointment', 'پماد'), ('cream', 'کرم'),
                        ('injection', 'آمپول / تزریق'), ('suppository', 'شیاف'),
                        ('inhaler', 'اسپری / استنشاقی'), ('spray', 'اسپری'),
                        ('powder', 'پودر'), ('patch', 'چسب'),
                        ('suspension', 'سوسپانسیون'), ('other', 'سایر'),
                    ],
                    max_length=20,
                    null=True,
                    verbose_name='فرم دارو',
                )),
                ('dosage', models.CharField(blank=True, max_length=100, null=True, verbose_name='دوز / مقدار')),
                ('frequency', models.CharField(
                    blank=True,
                    choices=[
                        ('once_daily', 'روزی یک بار'), ('twice_daily', 'روزی دو بار'),
                        ('three_daily', 'روزی سه بار'), ('four_daily', 'روزی چهار بار'),
                        ('every_6h', 'هر ۶ ساعت'), ('every_8h', 'هر ۸ ساعت'),
                        ('every_12h', 'هر ۱۲ ساعت'), ('weekly', 'هفته‌ای یک بار'),
                        ('twice_weekly', 'هفته‌ای دو بار'), ('monthly', 'ماهی یک بار'),
                        ('as_needed', 'در صورت نیاز'), ('once', 'فقط یک بار'),
                        ('continuous', 'مداوم / همیشه'), ('custom', 'سفارشی'),
                    ],
                    max_length=20,
                    null=True,
                    verbose_name='دوره مصرف',
                )),
                ('frequency_custom', models.CharField(blank=True, max_length=100, null=True, verbose_name='دوره سفارشی')),
                ('timing', models.CharField(
                    blank=True,
                    choices=[
                        ('before_meal', 'قبل از غذا'), ('after_meal', 'بعد از غذا'),
                        ('with_meal', 'همراه غذا'), ('empty_stomach', 'ناشتا'),
                        ('before_sleep', 'قبل از خواب'), ('morning', 'صبح'),
                        ('noon', 'ظهر'), ('evening', 'عصر'), ('night', 'شب'),
                        ('any', 'بدون محدودیت'),
                    ],
                    max_length=20,
                    null=True,
                    verbose_name='زمان مصرف',
                )),
                ('duration_value', models.PositiveIntegerField(blank=True, null=True, verbose_name='مدت')),
                ('duration_unit', models.CharField(
                    blank=True,
                    choices=[
                        ('day', 'روز'), ('week', 'هفته'), ('month', 'ماه'),
                        ('continuous', 'همیشه / مداوم'),
                    ],
                    max_length=20,
                    null=True,
                    verbose_name='واحد مدت',
                )),
                ('quantity', models.CharField(blank=True, max_length=50, null=True, verbose_name='تعداد کل')),
                ('instructions', models.TextField(blank=True, null=True, verbose_name='دستور / توضیحات')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('record', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='prescription_items',
                    to='patients.medicalrecord',
                    verbose_name='پرونده',
                )),
            ],
            options={
                'verbose_name': 'آیتم تجویز',
                'verbose_name_plural': 'آیتم‌های تجویز',
                'db_table': 'patients_prescription_item',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='prescriptionitem',
            index=models.Index(fields=['record', 'item_type'], name='patients_pre_record__idx'),
        ),
    ]

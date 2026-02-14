"""
مایگریشن داده‌های پیش‌فرض آزمایش‌ها، تصویربرداری‌ها و اقدامات درمانی
"""

from django.db import migrations


def seed_additional_terms(apps, schema_editor):
    """ایجاد داده‌های پیش‌فرض"""
    MedicalTerm = apps.get_model('patients', 'MedicalTerm')
    
    # ─── آزمایش‌های رایج ───
    lab_tests = [
        ('آزمایش خون کامل', 'CBC'),
        ('قند خون ناشتا', 'FBS'),
        ('قند خون تصادفی', 'BS'),
        ('هموگلوبین A1C', 'HbA1c'),
        ('چربی خون', 'Lipid Profile'),
        ('کلسترول', 'Cholesterol'),
        ('تری‌گلیسیرید', 'Triglyceride'),
        ('عملکرد کبد', 'LFT'),
        ('عملکرد کلیه', 'KFT'),
        ('اوره', 'BUN'),
        ('کراتینین', 'Creatinine'),
        ('اسید اوریک', 'Uric Acid'),
        ('آزمایش ادرار', 'Urinalysis'),
        ('کشت ادرار', 'Urine Culture'),
        ('تیروئید TSH', 'TSH'),
        ('تیروئید T3', 'T3'),
        ('تیروئید T4', 'T4'),
        ('آهن خون', 'Serum Iron'),
        ('فریتین', 'Ferritin'),
        ('ویتامین D', 'Vitamin D'),
        ('ویتامین B12', 'Vitamin B12'),
        ('کلسیم', 'Calcium'),
        ('منیزیم', 'Magnesium'),
        ('سدیم', 'Sodium'),
        ('پتاسیم', 'Potassium'),
        ('CRP', 'CRP'),
        ('ESR', 'ESR'),
        ('PSA', 'PSA'),
        ('آزمایش مدفوع', 'Stool Exam'),
        ('کشت خون', 'Blood Culture'),
        ('تست حاملگی', 'Pregnancy Test - βhCG'),
        ('آزمایش انعقادی', 'PT / PTT / INR'),
        ('گروه خون', 'Blood Group & Rh'),
        ('هپاتیت B', 'HBsAg'),
        ('هپاتیت C', 'HCV Ab'),
        ('HIV', 'HIV Ab'),
        ('رایت و کومبس رایت', 'Wright & Coombs Wright'),
        ('آمیلاز', 'Amylase'),
        ('لیپاز', 'Lipase'),
    ]
    
    # ─── تصویربرداری‌ها ───
    imaging = [
        ('سونوگرافی شکم و لگن', 'Abdominal & Pelvic Ultrasound'),
        ('سونوگرافی کلیه و مجاری', 'Renal Ultrasound'),
        ('سونوگرافی تیروئید', 'Thyroid Ultrasound'),
        ('سونوگرافی پستان', 'Breast Ultrasound'),
        ('سونوگرافی بارداری', 'Obstetric Ultrasound'),
        ('سونوگرافی داپلر', 'Doppler Ultrasound'),
        ('رادیوگرافی قفسه سینه', 'Chest X-Ray'),
        ('رادیوگرافی ستون فقرات', 'Spine X-Ray'),
        ('رادیوگرافی لگن', 'Pelvic X-Ray'),
        ('رادیوگرافی اندام', 'Extremity X-Ray'),
        ('رادیوگرافی سینوس', 'Sinus X-Ray'),
        ('سی‌تی اسکن مغز', 'Brain CT Scan'),
        ('سی‌تی اسکن قفسه سینه', 'Chest CT Scan'),
        ('سی‌تی اسکن شکم و لگن', 'Abdominopelvic CT Scan'),
        ('سی‌تی اسکن ستون فقرات', 'Spine CT Scan'),
        ('سی‌تی آنژیوگرافی', 'CT Angiography'),
        ('ام‌آر‌آی مغز', 'Brain MRI'),
        ('ام‌آر‌آی زانو', 'Knee MRI'),
        ('ام‌آر‌آی ستون فقرات', 'Spine MRI'),
        ('ام‌آر‌آی شکم', 'Abdominal MRI'),
        ('ماموگرافی', 'Mammography'),
        ('اکوکاردیوگرافی', 'Echocardiography'),
        ('نوار قلب', 'ECG / EKG'),
        ('هولتر قلب', 'Holter Monitor'),
        ('تست ورزش', 'Exercise Stress Test'),
        ('اسکن استخوان', 'Bone Scan'),
        ('اسکن تیروئید', 'Thyroid Scan'),
        ('نوار مغز', 'EEG'),
        ('نوار عصب و عضله', 'EMG / NCV'),
        ('آندوسکوپی', 'Endoscopy'),
        ('کولونوسکوپی', 'Colonoscopy'),
        ('اسپیرومتری', 'Spirometry'),
        ('آنژیوگرافی', 'Angiography'),
        ('دانسیتومتری استخوان', 'Bone Densitometry (DEXA)'),
    ]
    
    # ─── اقدامات درمانی ───
    procedures = [
        ('تزریق داخل مفصلی', 'Intra-articular Injection'),
        ('بخیه زخم', 'Wound Suturing'),
        ('تعویض پانسمان', 'Dressing Change'),
        ('فیزیوتراپی', 'Physiotherapy'),
        ('بیوپسی', 'Biopsy'),
        ('کرایوتراپی', 'Cryotherapy'),
        ('لیزرتراپی', 'Laser Therapy'),
        ('ختنه', 'Circumcision'),
        ('کشیدن دندان', 'Tooth Extraction'),
        ('تخلیه آبسه', 'Abscess Drainage'),
        ('گچ‌گیری', 'Casting'),
        ('اسپلینت', 'Splinting'),
        ('سرم‌تراپی', 'IV Fluid Therapy'),
        ('نبولایزر', 'Nebulizer'),
        ('لاواژ گوش', 'Ear Lavage'),
        ('تست آلرژی', 'Allergy Test'),
        ('واکسیناسیون', 'Vaccination'),
        ('تامپون بینی', 'Nasal Packing'),
        ('کاتتریزاسیون', 'Catheterization'),
        ('خال‌برداری', 'Mole Removal'),
    ]
    
    # ایجاد یکجا
    terms_to_create = []
    
    for name_fa, name_en in lab_tests:
        terms_to_create.append(MedicalTerm(
            category='lab_test',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    for name_fa, name_en in imaging:
        terms_to_create.append(MedicalTerm(
            category='imaging',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    for name_fa, name_en in procedures:
        terms_to_create.append(MedicalTerm(
            category='procedure',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    MedicalTerm.objects.bulk_create(terms_to_create, ignore_conflicts=True)


def reverse_seed(apps, schema_editor):
    MedicalTerm = apps.get_model('patients', 'MedicalTerm')
    MedicalTerm.objects.filter(
        category__in=['lab_test', 'imaging', 'procedure'],
        is_default=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0004_prescriptionitem'),
    ]

    operations = [
        migrations.RunPython(seed_additional_terms, reverse_seed),
    ]

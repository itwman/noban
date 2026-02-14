"""
مایگریشن داده‌های پیش‌فرض اصطلاحات پزشکی
علائم، تشخیص‌ها و داروهای رایج ایران
"""

from django.db import migrations


def seed_medical_terms(apps, schema_editor):
    """ایجاد داده‌های پیش‌فرض اصطلاحات پزشکی"""
    MedicalTerm = apps.get_model('patients', 'MedicalTerm')
    
    # ─── علائم / شکایات رایج ───
    symptoms = [
        ('سردرد', 'Headache'),
        ('تب', 'Fever'),
        ('سرفه', 'Cough'),
        ('گلودرد', 'Sore Throat'),
        ('تنگی نفس', 'Dyspnea'),
        ('درد قفسه سینه', 'Chest Pain'),
        ('درد شکم', 'Abdominal Pain'),
        ('تهوع', 'Nausea'),
        ('استفراغ', 'Vomiting'),
        ('اسهال', 'Diarrhea'),
        ('یبوست', 'Constipation'),
        ('سرگیجه', 'Dizziness'),
        ('ضعف و خستگی', 'Fatigue'),
        ('کمردرد', 'Back Pain'),
        ('درد مفاصل', 'Joint Pain'),
        ('درد عضلانی', 'Myalgia'),
        ('بی‌خوابی', 'Insomnia'),
        ('بثورات پوستی', 'Skin Rash'),
        ('خارش', 'Itching'),
        ('تورم', 'Swelling'),
        ('آبریزش بینی', 'Rhinorrhea'),
        ('عطسه', 'Sneezing'),
        ('درد گوش', 'Ear Pain'),
        ('کاهش اشتها', 'Loss of Appetite'),
        ('کاهش وزن', 'Weight Loss'),
        ('افزایش وزن', 'Weight Gain'),
        ('تپش قلب', 'Palpitation'),
        ('فشار خون بالا', 'Hypertension'),
        ('خونریزی بینی', 'Epistaxis'),
        ('درد دندان', 'Toothache'),
        ('سوزش سردل', 'Heartburn'),
        ('نفخ', 'Bloating'),
        ('تکرر ادرار', 'Frequent Urination'),
        ('سوزش ادرار', 'Dysuria'),
        ('لرز', 'Chills'),
        ('تعریق شبانه', 'Night Sweats'),
        ('تاری دید', 'Blurred Vision'),
        ('سوزش چشم', 'Eye Burning'),
        ('درد زانو', 'Knee Pain'),
        ('درد گردن', 'Neck Pain'),
        ('بی‌حسی و گزگز', 'Numbness and Tingling'),
        ('اضطراب', 'Anxiety'),
        ('افسردگی', 'Depression'),
    ]
    
    # ─── تشخیص‌های رایج ───
    diagnoses = [
        ('سرماخوردگی', 'Common Cold'),
        ('آنفولانزا', 'Influenza'),
        ('فارنژیت', 'Pharyngitis'),
        ('برونشیت', 'Bronchitis'),
        ('پنومونی', 'Pneumonia'),
        ('آسم', 'Asthma'),
        ('سینوزیت', 'Sinusitis'),
        ('اوتیت میانی', 'Otitis Media'),
        ('گاستریت', 'Gastritis'),
        ('رفلاکس معده', 'GERD'),
        ('کولیت', 'Colitis'),
        ('سنگ کلیه', 'Kidney Stone'),
        ('عفونت ادراری', 'UTI'),
        ('دیابت نوع ۲', 'Type 2 Diabetes'),
        ('فشار خون بالا', 'Hypertension'),
        ('هایپرلیپیدمی', 'Hyperlipidemia'),
        ('کم‌خونی فقر آهن', 'Iron Deficiency Anemia'),
        ('کم‌کاری تیروئید', 'Hypothyroidism'),
        ('پرکاری تیروئید', 'Hyperthyroidism'),
        ('میگرن', 'Migraine'),
        ('سردرد تنشی', 'Tension Headache'),
        ('آرتریت روماتوئید', 'Rheumatoid Arthritis'),
        ('آرتروز', 'Osteoarthritis'),
        ('دیسک کمر', 'Lumbar Disc Herniation'),
        ('اگزما', 'Eczema'),
        ('پسوریازیس', 'Psoriasis'),
        ('درماتیت تماسی', 'Contact Dermatitis'),
        ('عفونت قارچی', 'Fungal Infection'),
        ('ملتحمه', 'Conjunctivitis'),
        ('ویتیلیگو', 'Vitiligo'),
        ('واریس', 'Varicose Veins'),
        ('هموروئید', 'Hemorrhoids'),
        ('سندرم روده تحریک‌پذیر', 'IBS'),
        ('افسردگی', 'Major Depression'),
        ('اختلال اضطراب', 'Anxiety Disorder'),
        ('بیماری عروق کرونر', 'Coronary Artery Disease'),
        ('نارسایی قلبی', 'Heart Failure'),
        ('آلرژی فصلی', 'Seasonal Allergy'),
        ('ورتیگو', 'Vertigo'),
        ('نقرس', 'Gout'),
    ]
    
    # ─── داروهای رایج ایران ───
    medications = [
        ('استامینوفن ۳۲۵', 'Acetaminophen 325mg'),
        ('استامینوفن ۵۰۰', 'Acetaminophen 500mg'),
        ('استامینوفن کدئین', 'Acetaminophen Codeine'),
        ('ایبوپروفن ۲۰۰', 'Ibuprofen 200mg'),
        ('ایبوپروفن ۴۰۰', 'Ibuprofen 400mg'),
        ('ناپروکسن ۲۵۰', 'Naproxen 250mg'),
        ('دیکلوفناک ۲۵', 'Diclofenac 25mg'),
        ('دیکلوفناک ۵۰', 'Diclofenac 50mg'),
        ('آموکسی‌سیلین ۲۵۰', 'Amoxicillin 250mg'),
        ('آموکسی‌سیلین ۵۰۰', 'Amoxicillin 500mg'),
        ('آزیترومایسین ۲۵۰', 'Azithromycin 250mg'),
        ('آزیترومایسین ۵۰۰', 'Azithromycin 500mg'),
        ('سفالکسین ۲۵۰', 'Cephalexin 250mg'),
        ('سفالکسین ۵۰۰', 'Cephalexin 500mg'),
        ('سفیکسیم ۲۰۰', 'Cefixime 200mg'),
        ('سفیکسیم ۴۰۰', 'Cefixime 400mg'),
        ('مترونیدازول ۲۵۰', 'Metronidazole 250mg'),
        ('سیپروفلوکساسین ۵۰۰', 'Ciprofloxacin 500mg'),
        ('کوآموکسی‌کلاو ۶۲۵', 'Co-Amoxiclav 625mg'),
        ('سفتریاکسون', 'Ceftriaxone'),
        ('امپرازول ۲۰', 'Omeprazole 20mg'),
        ('پنتوپرازول ۴۰', 'Pantoprazole 40mg'),
        ('رانیتیدین ۱۵۰', 'Ranitidine 150mg'),
        ('متفورمین ۵۰۰', 'Metformin 500mg'),
        ('متفورمین ۱۰۰۰', 'Metformin 1000mg'),
        ('گلی‌بنکلامید', 'Glibenclamide'),
        ('آتورواستاتین ۲۰', 'Atorvastatin 20mg'),
        ('آتورواستاتین ۴۰', 'Atorvastatin 40mg'),
        ('لوزارتان ۲۵', 'Losartan 25mg'),
        ('لوزارتان ۵۰', 'Losartan 50mg'),
        ('آملودیپین ۵', 'Amlodipine 5mg'),
        ('آملودیپین ۱۰', 'Amlodipine 10mg'),
        ('آتنولول ۵۰', 'Atenolol 50mg'),
        ('هیدروکلروتیازید', 'Hydrochlorothiazide'),
        ('والزارتان ۸۰', 'Valsartan 80mg'),
        ('لووتیروکسین ۵۰', 'Levothyroxine 50mcg'),
        ('لووتیروکسین ۱۰۰', 'Levothyroxine 100mcg'),
        ('پردنیزولون ۵', 'Prednisolone 5mg'),
        ('دگزامتازون', 'Dexamethasone'),
        ('ستیریزین ۱۰', 'Cetirizine 10mg'),
        ('لوراتادین ۱۰', 'Loratadine 10mg'),
        ('کلرفنیرامین ۴', 'Chlorpheniramine 4mg'),
        ('دکسترومتورفان', 'Dextromethorphan'),
        ('دیفن‌هیدرامین', 'Diphenhydramine'),
        ('سالبوتامول اسپری', 'Salbutamol Inhaler'),
        ('فلوتیکازون اسپری', 'Fluticasone Inhaler'),
        ('آ.اس.آ ۸۰', 'ASA 80mg'),
        ('کلوپیدوگرل ۷۵', 'Clopidogrel 75mg'),
        ('وارفارین', 'Warfarin'),
        ('فروس سولفات', 'Ferrous Sulfate'),
        ('فولیک اسید ۱', 'Folic Acid 1mg'),
        ('ویتامین B12', 'Vitamin B12'),
        ('ویتامین D3', 'Vitamin D3'),
        ('کلسیم-D', 'Calcium-D'),
        ('مولتی‌ویتامین', 'Multivitamin'),
        ('دیازپام ۵', 'Diazepam 5mg'),
        ('آلپرازولام ۰.۵', 'Alprazolam 0.5mg'),
        ('فلوکستین ۲۰', 'Fluoxetine 20mg'),
        ('سرترالین ۵۰', 'Sertraline 50mg'),
        ('کربامازپین ۲۰۰', 'Carbamazepine 200mg'),
        ('گاباپنتین ۳۰۰', 'Gabapentin 300mg'),
        ('قطره چشمی بتامتازون', 'Betamethasone Eye Drop'),
        ('قطره بینی نرمال‌سالین', 'Normal Saline Nasal Drop'),
        ('پماد هیدروکورتیزون', 'Hydrocortisone Ointment'),
        ('پماد بتامتازون', 'Betamethasone Ointment'),
        ('کرم کلوتریمازول', 'Clotrimazole Cream'),
        ('سرم‌تراپی', 'IV Fluid Therapy'),
    ]
    
    terms = []
    
    for name_fa, name_en in symptoms:
        terms.append(MedicalTerm(
            category='symptom',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    for name_fa, name_en in diagnoses:
        terms.append(MedicalTerm(
            category='diagnosis',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    for name_fa, name_en in medications:
        terms.append(MedicalTerm(
            category='medication',
            name_fa=name_fa,
            name_en=name_en,
            is_default=True,
            usage_count=0,
        ))
    
    MedicalTerm.objects.bulk_create(terms, ignore_conflicts=True)


def reverse_seed(apps, schema_editor):
    """حذف داده‌های پیش‌فرض"""
    MedicalTerm = apps.get_model('patients', 'MedicalTerm')
    MedicalTerm.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0002_medicalterm'),
    ]

    operations = [
        migrations.RunPython(seed_medical_terms, reverse_seed),
    ]

"""
Template Tags برای تاریخ شمسی - نوبان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from django import template
from django.utils import timezone
import jdatetime
from datetime import datetime, date, time

register = template.Library()


# اعداد فارسی
PERSIAN_NUMBERS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
}

# نام روزهای هفته
WEEKDAY_NAMES = {
    0: 'شنبه',
    1: 'یکشنبه', 
    2: 'دوشنبه',
    3: 'سه‌شنبه',
    4: 'چهارشنبه',
    5: 'پنج‌شنبه',
    6: 'جمعه',
}

# نام ماه‌های شمسی
MONTH_NAMES = {
    1: 'فروردین',
    2: 'اردیبهشت',
    3: 'خرداد',
    4: 'تیر',
    5: 'مرداد',
    6: 'شهریور',
    7: 'مهر',
    8: 'آبان',
    9: 'آذر',
    10: 'دی',
    11: 'بهمن',
    12: 'اسفند',
}


def to_persian_numbers(text):
    """تبدیل اعداد انگلیسی به فارسی"""
    if text is None:
        return ''
    text = str(text)
    for en, fa in PERSIAN_NUMBERS.items():
        text = text.replace(en, fa)
    return text


def to_jalali(value):
    """تبدیل تاریخ میلادی به شمسی"""
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return jdatetime.datetime.fromgregorian(datetime=value)
    elif isinstance(value, date):
        return jdatetime.date.fromgregorian(date=value)
    
    return value


@register.filter(name='jalali')
def jalali_date(value, format_str='%Y/%m/%d'):
    """
    فیلتر تبدیل تاریخ به شمسی
    استفاده: {{ date|jalali }}
    یا با فرمت: {{ date|jalali:"%d %B %Y" }}
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            result = jalali.strftime(format_str)
            return to_persian_numbers(result)
    except:
        pass
    
    return value


@register.filter(name='jalali_full')
def jalali_full_date(value):
    """
    تاریخ کامل شمسی
    استفاده: {{ date|jalali_full }}
    خروجی: چهارشنبه، ۱۵ بهمن ۱۴۰۴
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            weekday = WEEKDAY_NAMES.get(jalali.weekday(), '')
            day = to_persian_numbers(jalali.day)
            month = MONTH_NAMES.get(jalali.month, '')
            year = to_persian_numbers(jalali.year)
            return f'{weekday}، {day} {month} {year}'
    except:
        pass
    
    return value


@register.filter(name='jalali_short')
def jalali_short_date(value):
    """
    تاریخ کوتاه شمسی
    استفاده: {{ date|jalali_short }}
    خروجی: ۱۴۰۴/۱۱/۱۵
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            return to_persian_numbers(f'{jalali.year}/{jalali.month:02d}/{jalali.day:02d}')
    except:
        pass
    
    return value


@register.filter(name='jalali_date_only')
def jalali_date_only(value):
    """
    فقط روز و ماه
    استفاده: {{ date|jalali_date_only }}
    خروجی: ۱۵ بهمن
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            day = to_persian_numbers(jalali.day)
            month = MONTH_NAMES.get(jalali.month, '')
            return f'{day} {month}'
    except:
        pass
    
    return value


@register.filter(name='jalali_datetime')
def jalali_datetime(value):
    """
    تاریخ و ساعت شمسی
    استفاده: {{ datetime|jalali_datetime }}
    خروجی: ۱۴۰۴/۱۱/۱۵ - ۱۴:۳۰
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            date_str = f'{jalali.year}/{jalali.month:02d}/{jalali.day:02d}'
            time_str = f'{jalali.hour:02d}:{jalali.minute:02d}'
            return to_persian_numbers(f'{date_str} - {time_str}')
    except:
        pass
    
    return value


@register.filter(name='jalali_time')
def jalali_time(value):
    """
    فقط ساعت
    استفاده: {{ time|jalali_time }}
    خروجی: ۱۴:۳۰
    """
    if value is None:
        return ''
    
    try:
        if isinstance(value, time):
            return to_persian_numbers(f'{value.hour:02d}:{value.minute:02d}')
        elif isinstance(value, datetime):
            return to_persian_numbers(f'{value.hour:02d}:{value.minute:02d}')
    except:
        pass
    
    return value


@register.filter(name='persian_number')
def persian_number(value):
    """
    تبدیل عدد به فارسی
    استفاده: {{ number|persian_number }}
    """
    return to_persian_numbers(value)


@register.filter(name='weekday_name')
def weekday_name(value):
    """
    نام روز هفته شمسی
    استفاده: {{ date|weekday_name }}
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            return WEEKDAY_NAMES.get(jalali.weekday(), '')
    except:
        pass
    
    return value


@register.filter(name='month_name')
def month_name(value):
    """
    نام ماه شمسی
    استفاده: {{ date|month_name }}
    """
    if value is None:
        return ''
    
    try:
        jalali = to_jalali(value)
        if jalali:
            return MONTH_NAMES.get(jalali.month, '')
    except:
        pass
    
    return value


@register.filter(name='time_ago')
def time_ago(value):
    """
    زمان گذشته به صورت فارسی
    استفاده: {{ datetime|time_ago }}
    خروجی: ۵ دقیقه پیش، دیروز، ۲ روز پیش
    """
    if value is None:
        return ''
    
    try:
        now = timezone.now()
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())
            value = timezone.make_aware(value)
        
        diff = now - value
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'همین الان'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{to_persian_numbers(minutes)} دقیقه پیش'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{to_persian_numbers(hours)} ساعت پیش'
        elif seconds < 172800:
            return 'دیروز'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{to_persian_numbers(days)} روز پیش'
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f'{to_persian_numbers(weeks)} هفته پیش'
        else:
            return jalali_short_date(value)
    except:
        pass
    
    return value


@register.filter(name='time_until')
def time_until(value):
    """
    زمان باقی‌مانده به صورت فارسی
    استفاده: {{ datetime|time_until }}
    خروجی: ۵ دقیقه دیگر، فردا، ۲ روز دیگر
    """
    if value is None:
        return ''
    
    try:
        now = timezone.now()
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())
            value = timezone.make_aware(value)
        
        diff = value - now
        seconds = diff.total_seconds()
        
        if seconds < 0:
            return 'گذشته'
        elif seconds < 60:
            return 'کمتر از یک دقیقه'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{to_persian_numbers(minutes)} دقیقه دیگر'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{to_persian_numbers(hours)} ساعت دیگر'
        elif seconds < 172800:
            return 'فردا'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{to_persian_numbers(days)} روز دیگر'
        else:
            return jalali_short_date(value)
    except:
        pass
    
    return value


@register.simple_tag
def jalali_today():
    """
    تاریخ امروز شمسی
    استفاده: {% jalali_today %}
    """
    today = jdatetime.date.today()
    weekday = WEEKDAY_NAMES.get(today.weekday(), '')
    day = to_persian_numbers(today.day)
    month = MONTH_NAMES.get(today.month, '')
    year = to_persian_numbers(today.year)
    return f'{weekday}، {day} {month} {year}'


@register.simple_tag
def jalali_now():
    """
    تاریخ و ساعت فعلی شمسی
    استفاده: {% jalali_now %}
    """
    now = jdatetime.datetime.now()
    date_str = f'{now.year}/{now.month:02d}/{now.day:02d}'
    time_str = f'{now.hour:02d}:{now.minute:02d}'
    return to_persian_numbers(f'{date_str} - {time_str}')


@register.filter(name='price_format')
def price_format(value):
    """
    فرمت قیمت به تومان
    استفاده: {{ price|price_format }}
    خروجی: ۲۵۰,۰۰۰ تومان
    """
    if value is None:
        return ''
    
    try:
        value = int(value)
        formatted = '{:,}'.format(value)
        return to_persian_numbers(formatted) + ' تومان'
    except:
        pass
    
    return value


@register.filter(name='phone_format')
def phone_format(value):
    """
    فرمت شماره تلفن
    استفاده: {{ phone|phone_format }}
    خروجی: ۰۹۱۲-۳۴۵-۶۷۸۹
    """
    if value is None:
        return ''
    
    try:
        value = str(value).replace(' ', '').replace('-', '')
        if len(value) == 11:
            formatted = f'{value[:4]}-{value[4:7]}-{value[7:]}'
            return to_persian_numbers(formatted)
    except:
        pass
    
    return to_persian_numbers(value)

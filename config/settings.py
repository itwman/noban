"""
Django settings for NoBan project.

نرم‌افزار نوبان - سیستم رزرو و مدیریت نوبت پزشکان
توسعه‌دهنده: شرکت توسعه هوشمند فرش ایرانیان
"""

from pathlib import Path
import os
from decouple import config
import pymysql

# PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# If ALLOWED_HOSTS contains '*', allow all
if '*' in ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']


# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party Apps
    'rest_framework',
    'corsheaders',
    'django_jalali',
    'channels',
    
    # Local Apps
    'apps.core',
    'apps.accounts',
    'apps.doctors',
    'apps.clinics',
    'apps.appointments',
    'apps.patients',
    'apps.payments',
    'apps.notifications',
    'apps.queue',
    'apps.reports',
    'apps.secretary',
    'installer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': config('DB_NAME', default='noban_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==============================================================================
# INTERNATIONALIZATION (Persian/Farsi)
# ==============================================================================

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Persian Number Format
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '٬'  # Persian thousand separator


# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# ==============================================================================
# MEDIA FILES (User Uploads)
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# MULTI-TENANT CONFIGURATION
# ==============================================================================

MULTI_TENANT_ENABLED = config('MULTI_TENANT_ENABLED', default=False, cast=bool)


# ==============================================================================
# DJANGO REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
}


# ==============================================================================
# CORS SETTINGS
# ==============================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add production CORS origins
SITE_URL_VALUE = config('SITE_URL', default='http://localhost:8000')
if SITE_URL_VALUE not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(SITE_URL_VALUE)

CORS_ALLOW_CREDENTIALS = True

# Allow all origins in development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# ==============================================================================
# CHANNELS CONFIGURATION (WebSocket)
# ==============================================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(
                config('REDIS_HOST', default='localhost'),
                config('REDIS_PORT', default=6379, cast=int)
            )],
        },
    },
}


# ==============================================================================
# PAYMENT GATEWAY SETTINGS
# ==============================================================================

# ZarinPal
ZARINPAL_MERCHANT_ID = config('ZARINPAL_MERCHANT_ID', default='')
ZARINPAL_SANDBOX = config('ZARINPAL_SANDBOX', default=True, cast=bool)
ZARINPAL_CALLBACK_URL = config('SITE_URL', default='http://localhost:8000') + '/payments/zarinpal/verify/'

# Drik
DRIK_API_KEY = config('DRIK_API_KEY', default='')
DRIK_SANDBOX = config('DRIK_SANDBOX', default=True, cast=bool)
DRIK_CALLBACK_URL = config('SITE_URL', default='http://localhost:8000') + '/payments/drik/verify/'


# ==============================================================================
# SMS SETTINGS (sms.ir)
# ==============================================================================

SMS_API_KEY = config('SMS_API_KEY', default='')
SMS_LINE_NUMBER = config('SMS_LINE_NUMBER', default='')


# ==============================================================================
# APPLICATION SETTINGS
# ==============================================================================

SITE_URL = config('SITE_URL', default='http://localhost:8000')
SITE_NAME = config('SITE_NAME', default='نوبان - سیستم نوبت‌دهی پزشکان')


# ==============================================================================
# EMAIL CONFIGURATION (Optional)
# ==============================================================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')


# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# CSRF
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_TRUSTED_ORIGINS = [config('SITE_URL', default='http://localhost:8000')]

# Session
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 86400  # 24 hours

# XSS Protection
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# X-Frame-Options
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Production Security
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False  # Handled by reverse proxy
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==============================================================================
# WHITENOISE (Static Files in Production)
# ==============================================================================

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' if not DEBUG else 'django.contrib.staticfiles.storage.StaticFilesStorage'


# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if not exists
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# CUSTOM USER MODEL
# ==============================================================================

AUTH_USER_MODEL = 'accounts.User'


# ==============================================================================
# LOGIN/LOGOUT URLS
# ==============================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

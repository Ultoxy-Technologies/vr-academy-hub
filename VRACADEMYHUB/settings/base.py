from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-l-zq3uu6&^46d2#2e0=x%3dvs+d)iw&h0qq)ha1h$a&_$pumt4'

# APPLICATIONS
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'WebApp',
    'AdminApp',
    'StudentApp',
    'SoftwareApp',

    'crispy_forms',
    'crispy_bootstrap5',
    'simple_history',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VRACADEMYHUB.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'VRACADEMYHUB.wsgi.application'

# AUTH
AUTH_USER_MODEL = 'AdminApp.CustomUser'
LOGIN_URL = '/login'

# INTERNATIONALIZATION
LANGUAGES = [
    ('en', _('English')),
    ('hi', _('Hindi')),
    ('mr', _('Marathi')),
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# STATIC & MEDIA
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'

# CRISPY
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JAZZMIN
JAZZMIN_SETTINGS = {
    "site_title": "VR ACADEMY HUB",
    "site_header": "VR ACADEMY HUB",
    "site_brand": "VR ACADEMY HUB",
    "welcome_sign": "Welcome to VR ACADEMY HUB Dashboard",
    "copyright": "© 2025 VR Training Academy",
    "site_logo": "website/img/logo.png",
    "login_logo": "website/img/logo-for-admin-login.png",
    "theme": "pulse",
    "icons": {
        "auth": "fas fa-users-cog",
        "AdminApp.CustomUser": "fas fa-user-shield",
        "AdminApp.CRMFollowup": "fas fa-headset",
        "AdminApp.CRM_Student_Interested_for_options": "fas fa-graduation-cap",
        "AdminApp.Branch": "fas fa-building",
        "AdminApp.Enquiry": "fas fa-envelope-open-text",
        "AdminApp.Event": "fas fa-calendar-alt",
        "AdminApp.EventRegistration": "fas fa-id-card",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark bg-primary",
    "accent": "accent-primary",
    "theme": "pulse",
}

CSRF_TRUSTED_ORIGINS = [
    'https://vracademyhub.com',
    'https://www.vracademyhub.com',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST FRAMEWORK & JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}

# EMAIL DEFAULTS
DEFAULT_FROM_EMAIL = 'VR Academy Hub <prameshwar4378@gmail.com>'
SERVER_EMAIL = 'prameshwar4378@gmail.com'
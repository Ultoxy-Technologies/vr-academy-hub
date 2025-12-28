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
]

MIDDLEWARE = [
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
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
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
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark bg-primary",
    "accent": "accent-primary",
    "theme": "pulse",
}

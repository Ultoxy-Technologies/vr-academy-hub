from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production api keys
RAZORPAY_KEY_ID = 'rzp_live_S0GtEF2P4Jr7SY' 
#Production api secret keys
RAZORPAY_KEY_SECRET = 'RLFz6G1j9CgStlwKDFyBIqPK'

import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'file': {
            'level': 'ERROR',   # log only ERROR and CRITICAL
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'formatter': 'verbose',
        },
    },

    'loggers': {
        # Django internal errors
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },

        # Catch errors from your apps
        '': {  # root logger
            'handlers': ['file'],
            'level': 'ERROR',
        },
    },
}



# #test api keys
# RAZORPAY_KEY_ID = 'rzp_test_RfELpk3eZdngJZ' 
# #test api secret keys
# RAZORPAY_KEY_SECRET = 'lWVYlpQE8ftiRcrmfv1M8arF'


# Email Configuration (SMTP with environment variable override)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'prameshwar4378@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'rxfv klps utdv tiro')
DEFAULT_FROM_EMAIL = f"VR Academy Hub <{EMAIL_HOST_USER}>"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Local static & media
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'


# Timezone settings for India
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True


LANGUAGE_CODE = 'en-in'  # English for India
USE_I18N = True
USE_L10N = True

USE_L10N = False 

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
# RAZORPAY_KEY_ID = 'rzp_live_S0GtEF2P4Jr7SY' 
# #Production api secret keys
# RAZORPAY_KEY_SECRET = 'RLFz6G1j9CgStlwKDFyBIqPK'




#test api keys
RAZORPAY_KEY_ID = 'rzp_test_RfELpk3eZdngJZ' 
#test api secret keys
RAZORPAY_KEY_SECRET = 'lWVYlpQE8ftiRcrmfv1M8arF'


# Email (optional: console backend for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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

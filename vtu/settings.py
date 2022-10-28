"""
Django settings for vtu project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s^$@n8c&gso%x540m3*0300#7tky#1^4v@#_r9x*zxn&8v@@ok'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition


INSTALLED_APPS = [
    'threadedcomments',
    'django_comments',
    'app',
    'crispy_forms',
    "bootstrapform",
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'notifications',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    #'adminrestrict',

    'django.contrib.sites',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'session_security',
    'logentry_admin',
     'django_otp',
    'django_otp.plugins.otp_totp',

    'colorfield',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,

      'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
}

LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_EMAIL_VERIFICATION = "optional"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

     'django_otp.middleware.OTPMiddleware',
    #'adminrestrict.middleware.AdminPagesRestrictMiddleware',
     'session_security.middleware.SessionSecurityMiddleware',
]

ROOT_URLCONF = 'vtu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #"app.context_processors.categories_processor",

            ],
        },
    },
]

WSGI_APPLICATION = 'vtu.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "app.CustomUser"
LOGOUT_REDIRECT_URL = 'home'
LOGIN_REDIRECT_URL = 'profile'
LOGIN_URL= 'login'


CRISPY_TEMPLATE_PACK = 'bootstrap4'

SITE_ID = 1
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_INSECURE = True
SESSION_SECURITY_EXPIRE_AFTER = 172800


EMAIL_FILE_PATH = os.path.join(BASE_DIR,'sent_emails')


#################################################### EMAIL TYPES ####################################################
# 1 - Cpanel

# EMAIL SETTING START
"""
if DEBUG == True:
     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.yuniqtelecoms.com'
EMAIL_HOST_USER = 'support@yuniqtelecoms.com'
EMAIL_HOST_PASSWORD = 'Fawaz2000'
DEFAULT_FROM_EMAIL = 'support@yuniqtelecoms.com'
SERVER_EMAIL = 'support@yuniqtelecoms.com'
EMAIL_PORT = 26
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_FILE_PATH = os.path.join(BASE_DIR,'sent_emails')
# EMAIL SETTING END
"""



# 2 - Namecheap Private Email
"""
# EMAIL SETTING START
if DEBUG == True:
     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_HOST_USER = 'support@yuniqtelecoms.com'
EMAIL_HOST_PASSWORD = 'Hameed2021'
DEFAULT_FROM_EMAIL = 'support@yuniqtelecoms.com'
SERVER_EMAIL = 'support@yuniqtelecoms.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_FILE_PATH = os.path.join(BASE_DIR,'sent_emails')
# EMAIL SETTING END
"""

#  EMAIL TYPE THREE
"""
EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_API_KEY =  "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"
DEFAULT_FROM_EMAIL ='noreply@yuniqtelecoms.com'
#twili +17854917497
TWILIO_ACCOUNT_SID = 'AC595310278fa79275fbce4cc73d0c795d'
TWILIO_AUTH_TOKEN= '8edad17593a6a9847474747cb92fa353'
TWILIO_DEFAULT_CALLERID ='+17854917497'

"""

# MAILGUN
"""
if DEBUG == True:
     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
     
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'postmaster@mymail.yuniqtelecoms.com'
EMAIL_HOST_USER = 'postmaster@mymail.yuniqtelecoms.com'
SERVER_EMAIL = 'postmaster@mymail.yuniqtelecoms.com'
EMAIL_HOST_PASSWORD = '100329516a1be7bf25e242dbd6411900-e31dc3cc-31c5b76e'
EMAIL_USE_TLS = True
"""


DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
       'file': {
        #    'level': 'DEBUG',
           'level': 'INFO',
           'class': 'logging.FileHandler',
           'filename': 'habeeb_log.txt',
       },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            # 'handlers': ['console','file'],
            # 'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'handlers': ['file'],
            'level': "INFO",
        },
    },
}

STATIC_FILES_DIRS =['static']
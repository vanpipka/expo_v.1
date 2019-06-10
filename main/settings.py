"""
Django settings for expo project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json
#from main.models import CompanySettings

USE_I18N = True
USE_L10N = False

LANGUAGE_CODE = 'ru-RU'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Прочитаем настройки из файла
SETTINGS_DIR = os.path.join(BASE_DIR, 'expo_settings')
#
with open(os.path.join(SETTINGS_DIR, 'settings.json'), 'r') as f:

    try:
        struct = json.loads(f.read())

        SECRET_KEY      = struct.get('SECRET_KEY', '')
        DEBUG           = struct.get('DEBUG', False)
        ALLOWED_HOSTS   = struct.get('ALLOWED_HOSTS', '')
        HOME_PAGE       = struct.get('HOME_PAGE', '')
        STATIC_ROOT     = os.path.join(BASE_DIR, struct.get('STATIC', ''))
        STATIC_URL      = struct.get('STATIC_HOST', '')
        MEDIA_ROOT      = os.path.join(BASE_DIR, struct.get('MEDIA', ''))
        MEDIA_URL       = struct.get('MEDIA_HOST', '')

        #print(struct)
    except json.JSONDecodeError:
        SECRET_KEY      = ''
        DEBUG           = False
        ALLOWED_HOSTS   = ''
        HOME_PAGE       = ''
        #STATIC_ROOT     = os.path.join(BASE_DIR, 'static')
        #STATIC_URL      = 'static/'
        MEDIA_ROOT      = os.path.join(BASE_DIR, 'media')
        MEDIA_URL       = 'media/   '

#STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
#STATIC_URL = '/static/'

#print(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '6i0a)qi2!4&^(c7ie2@_v1y2w^sq##9+ilw)3^v!d5&xuh)=3a'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True

#ALLOWED_HOSTS = ['10.10.48.201', 'vpn2.contrail.ru', 'cs.itoe.ru', 'py.itoe.ru']


# Application definition

INSTALLED_APPS = [

    #'channels',
    #'allauth.socialaccount.providers.vk',
    #'allauth.socialaccount.providers.odnoklassniki',
    #'allauth.socialaccount.providers.auth0',
    #'send_email.apps.SendEmailConfig',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'expo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

)

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/login/"

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
#}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
		'NAME': 'vseexpo',
        'USER': 'django',
        'PASSWORD': 'Io89yHP>',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
    },
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'

TIME_ZONE = 'Europe/Moscow'

USE_TZ = True

USE_I18N = True

USE_L10N = True

SITE_ID = 2
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

with open(os.path.join(SETTINGS_DIR, 'companysettings.json'), 'r') as f:

    try:
        struct = json.loads(f.read())
        COMPANY_ADDRESS = struct.get('address', '')  # "117452 г.Москва, ул.Азовская, 24/3"
        COMPANY_PHONE   = struct.get('phone', '')  # "8 8 (800) 555-55-55"
        COMPANY_EMAIL   = struct.get('email', '')  # "info@vseexpo.ru"

    except json.JSONDecodeError:
        COMPANY_ADDRESS = ''  # "117452 г.Москва, ул.Азовская, 24/3"
        COMPANY_PHONE   = ''  # "8 8 (800) 555-55-55"
        COMPANY_EMAIL   = ''  # "info@vseexpo.ru"

#MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
#MEDIA_URL = '/media/'

#EMAIL_USE_TLS = True
#EMAIL_HOST = 'mail.mmss.ltd'
#EMAIL_PORT = 25
#EMAIL_HOST_USER = 'info@mmss.ltd'
#EMAIL_HOST_PASSWORD = 'ieh7w2k'
#DEFAULT_FROM_EMAIL = 'info@mmss.ltd'
#DEFAULT_TO_EMAIL = 'info@mmss.ltd'

LOG_FILE = os.path.join(SETTINGS_DIR, 'vseexpo.log')

LOGGING = {
   'version': 1,
   'disable_existing_loggers': False,
   'handlers': {
       'file': {
           'level': 'INFO',
           'class': 'logging.FileHandler',
           'filename': LOG_FILE,
       },
   },
   'loggers': {
       'django': {
           'handlers': ['file'],
           'level': 'INFO',
           'propagate': True,
       },
   },
}

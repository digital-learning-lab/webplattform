"""
Django settings for dll project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from environs import Env
env = Env()



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'SET_ME')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', ['*'])

# DJANGO_ADMINS=John:john@admin.com,Jane:jane@admin.com
ADMINS = [x.split(':') for x in env.list('DJANGO_ADMINS', [])]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'webpack_loader',
    'easy_thumbnails',
    'filer',
    'mptt',
    'meta',
    'taggit',
    'polymorphic',
    'django_extensions',
    'crispy_forms',
    'ckeditor',
    'dll.content',
    'dll.user',
    'dll.general',
    'dll.communication',
    'rest_framework',
    'django_filters',
    'rules.apps.AutodiscoverRulesConfig',
    'haystack'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
]

ROOT_URLCONF = 'dll.configuration.urls'

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

WSGI_APPLICATION = 'dll.configuration.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DATABASE_NAME'),
        'USER': env.str('DATABASE_USER'),
        'HOST': env.str('DATABASE_HOST'),
        'PORT': env.int('DATABASE_PORT', 5432),
    }
}
if env.str('DATABASE_PASSWORD', None):
    DATABASES['default']['PASSWORD'] = env.str('DATABASE_PASSWORD')


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = os.getenv('STATIC_URL') or '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT') or os.path.join(BASE_DIR, '..', 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'dist/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, './static/dist/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}

MEDIA_URL = os.getenv('MEDIA_URL') or '/media/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT') or os.path.join(BASE_DIR, 'media')

AUTH_USER_MODEL = 'user.DllUser'
AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',  # this is default
)

DEFAULT_USER_USERNAME = 'TUHH'
DEFAULT_USER_EMAIL = 'digital.learning.lab@tuhh.de'
DEFAULT_USER_PASSWORD = '?&~ pCYqyj2Q4]/a?w#P`'
SHELL_PLUS = "bpython"  # bpython does not work on pycharm terminal. use plain

TAGGIT_CASE_INSENSITIVE = True

SITE_ID = 1  # this is for django-flatpages

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'dll': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'default_from_email@tuhh.de'  # todo: default from email address

LOGIN_URL = 'user:login'
LOGIN_REDIRECT_URL = 'user:profile'
LOGOUT_REDIRECT_URL = 'home'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'SEARCH_PARAM': 'q',
    'DEFAULT_PERMISSION_CLASSES': []
}

CONTACT_EMAIL_BSB = "stabsstelle-digitalisierung@bsb.hamburg.de"
CONTACT_EMAIL_DLL = "digital.learning.lab@tuhh.de"
VALIDATE_RECAPTCHA = False

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://{hostname}:6379/0'.format(
    hostname=env.str('REDIS_HOSTNAME'),
))
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://{}:8983/solr/mycore'.format(env.str('SOLR_HOSTNAME')),
        'ADMIN_URL': 'http://{}:8983/solr/admin/cores'.format(env.str('SOLR_HOSTNAME'))
    },
}

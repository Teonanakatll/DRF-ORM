"""
Django settings for books project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
import sys
from pathlib import Path

# from gpt4.utils import cons

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5x-6)j+or@=(+ys(e5w$_1&vhp#7ke^uak!9x3=ksl$!7s+-ck'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'rest_framework',
    'django_filters',
    'social_django',
    # красивая консоль,  python manage.py shell_plus --ipythonj
    # python manage.py show_urls | findstr /V "admin"  python manage.py reset_db

    'django_extensions',

    # авторизация djoser и таблицами drf
    'rest_framework.authtoken',
    'djoser',

    'store.apps.StoreConfig',
    'gpt4.apps.Gpt4Config',
    'web_scraper.apps.WebScraperConfig',
    'bot.apps.BotConfig',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',

    # django-debug-toolbar-force, вывести gebug_toolbar на странице с json в конце урла - ?debug-toolbar &debug-toolbar
    'debug_toolbar_force.middleware.ForceDebugToolbarMiddleware',
]

ROOT_URLCONF = 'books.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'books.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'books_db3',
        'USER': 'home',
        'PASSWORD': 'home',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}


AUTHENTICATION_BACKENDS = (
    # 'social_core.backends.open_id.OpenIdAuth',
    # 'social_core.backends.google.GoogleOpenId',
    # 'social_core.backends.google.GoogleOAuth2',
    # 'social_core.backends.google.GoogleOAuth',
    # 'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.yahoo.YahooOpenId',

    'social_core.backends.github.GithubOAuth2',

    # базовый бэкэнд джонго обязательно прописать
    'django.contrib.auth.backends.ModelBackend',
)


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.SessionAuthentication',
    # ],

    # авторизация с djoser и стандартными таблицами токенов drf
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    # фильтры django_filters
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    # дефолтный формат для вывода данных

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],


}

# разрешаем social_django использовать json поле postgress
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

# ключи github для доступа к его авторизации
SOCIAL_AUTH_GITHUB_KEY = 'Ov23litrALJlHHi2KtL7'
SOCIAL_AUTH_GITHUB_SECRET = 'd5df97a8a1ec38e1565b126263d691f348f9da72'

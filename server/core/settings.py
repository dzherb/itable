from collections.abc import Sequence
import datetime
import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

TRUE_VALUES = ('true', 'y')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = os.getenv('DJANGO_DEBUG', '').lower() in TRUE_VALUES

ALLOWED_HOSTS: Sequence[str] = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.users.apps.UsersConfig',
    'apps.investment_tables.apps.InvestmentTablesConfig',
    'apps.portfolios.apps.PortfolioConfig',
    'apps.exchange.apps.ExchangeConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.users.authentication.middleware.JWTAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.ItableUser'
AUTHENTICATION_BACKENDS = [
    'apps.users.authentication.backends.JWTAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static' / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ugly solution to pass BASE_DIR to the setup_logging function.
# Unfortunately Django doesn't give much flexibility
# with the LOGGING_CONFIG callable path.
LOGGING = BASE_DIR
LOGGING_CONFIG = 'logger.setup.setup'

# Disable logging while running tests
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

RUN_BACKGROUND_TASKS = os.getenv('RUN_BACKGROUND_TASKS', 'y') in TRUE_VALUES

ACCESS_TOKEN_TIME_TO_LIVE = datetime.timedelta(
    minutes=int(os.getenv('ACCESS_TOKEN_TIME_TO_LIVE_IN_MINUTES', '10')),
)
REFRESH_TOKEN_TIME_TO_LIVE = datetime.timedelta(
    days=int(os.getenv('REFRESH_TOKEN_TIME_TO_LIVE_IN_DAYS', '30')),
)

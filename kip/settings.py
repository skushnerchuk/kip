import logging
import os
import sys
from datetime import timedelta

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DNS', ''),
    integrations=[DjangoIntegration()]
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            '41j6lwa3&%qww!)o!o_8oom^o&%ul=bu1jldq51erh$v-o3l-m')

# По умолчанию отключаем отладку. Для ее включения надо выставить ее равной 1
# в текущем окружении
DEBUG = int(os.environ.get('DEBUG', 0))
TESTING = (len(sys.argv) > 1 and sys.argv[1].lower() == 'test') or \
          ('pytest' in sys.argv[0].lower())
if TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# В режиме отладки переменные окружения берем из файла
# Существующие - будут перезаписаны
if DEBUG:
    load_dotenv('.env')

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kip_api.apps.KipApiConfig',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'admin_reorder',
]
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'kip_api.middleware.MonitoringMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'kip.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'kip.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kip',
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
        'TEST': {
            'NAME': 'kip_test'
        }
    }
}

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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = 'static'
STATIC_URL = '/static/'

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
#     os.path.join(BASE_DIR, 'static/images'),
# ]

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'kip_api.handlers.core_exception_handler',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append('rest_framework.renderers.BrowsableAPIRenderer')

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000/')
API_URL = 'api/v1/'
ACCESS_TOKEN_LIMIT = int(os.environ.get('ACCESS_TOKEN_LIMIT', 15))
REFRESH_TOKEN_LIMIT = int(os.environ.get('REFRESH_TOKEN_LIMIT', 30))

if DEBUG:
    ACCESS_TOKEN_LIMIT = 600
    REFRESH_TOKEN_LIMIT = 365

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_LIMIT),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=REFRESH_TOKEN_LIMIT),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'pk',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

AUTH_USER_MODEL = "kip_api.User"

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
}

ADMIN_REORDER = (
    'token_blacklist',
    'kip_api',
    {'app': 'kip_api', 'models': ('auth.User',)},
    {'app': 'auth', 'models': ('kip_api.User', 'auth.Group')},
)
INFORMER_EMAIL = 'info@example.com'

#
# Все логи пишем в stdout. Так как работа приложения планируется в контейнере,
# то логи будем собирать из контейнеров централизованно через FluentD

# Для выполнения тестов рекомендуется выставить FULL_DISABLE_LOGGING = True
DISABLE_LOGGING = True
# Логи будем готовить сами, логи django нас не интересуют
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

LOGGING_LEVEL = int(os.environ.get('LOGGING_LEVEL', logging.DEBUG))

logging.basicConfig(
    level=LOGGING_LEVEL,
    handlers=[logging.StreamHandler(sys.stdout)],
    format='%(message)s'
)
# Гасим логи от factory_boy, они нам не нужны
logging.getLogger('factory').setLevel(logging.ERROR)
logging.getLogger('faker').setLevel(logging.ERROR)

# Настройки для работы с медиа
MEDIA_URL = '/images/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(BASE_DIR, 'images'))
DEFAULT_AVATAR = ''.join([MEDIA_URL, 'default_avatar.jpeg'])
MAX_AVATAR_SIZE = int(os.getenv('MAX_AVATAR_SIZE', 2 * 1024 * 1024))
APPEND_SLASH = False

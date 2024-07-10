"""
Django settings for careconnect project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w8c2hne=jtg&*_v%0v@u!ch+0@1@4(g*xwwbznr)o^)_de3k%n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# AUTH_USER_MODEL = 'accounts.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'drf_yasg',
    'daphne',
    'django.contrib.staticfiles',
    'accounts',
    'healthcare',
    'rest_framework',
    'rest_framework_mongoengine',
    'channels',
]
ASGI_APPLICATION = 'careconnect.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'careconnect.urls'

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

WSGI_APPLICATION = 'careconnect.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

import mongoengine

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

# MongoEngine settings
MONGODB_DATABASES = {
    'default': {
        'name': 'careconnect',  # Your MongoDB database name
        'host': 'db',   # MongoDB host
        'port': 27017,         # MongoDB port
        'username': '',        # If authentication is enabled
        'password': '',
        'authentication_source': 'admin',
        'connect': False,      # Connect to MongoDB on start
    },
}

mongoengine.connect(
    db=MONGODB_DATABASES['default']['name'],
    # host=MONGODB_DATABASES['default']['host'],
    # host="mongodb://db:27017/careconnect",
    # host="db",
    host=f"mongodb://{MONGODB_DATABASES['default']['host']}:{MONGODB_DATABASES['default']['port']}",
    port=MONGODB_DATABASES['default']['port'],
    username=MONGODB_DATABASES['default']['username'],
    password=MONGODB_DATABASES['default']['password'],
    authentication_source=MONGODB_DATABASES['default']['authentication_source']
)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27018/careconnect')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django authentication backend
    'accounts.authentication.JWTAuthentication',    # Custom JWT authentication backend
]

# REST Framework settings (optional, if using)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # For session-based authentication
        'rest_framework.authentication.TokenAuthentication',  # Optional: Token authentication
        'accounts.authentication.JWTAuthentication',  # Custom JWT authentication
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

JWT_SECRET_KEY = 'your_jwt_secret_key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 28800  # 8 hours

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

import os

STATIC_URL = '/static/'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'darains.brainerhub@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'kbjt mtal webt xwqd'  # Replace with your Google Generated App Password


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    }
}

#channels settings
ASGI_APPLICATION = 'careconnect.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}

CHANNELS_MIDDLEWARE = [
    'channels.middleware.auth.AuthenticationMiddleware',
    'channels.middleware.websocket.WebSocketMiddleware',
]
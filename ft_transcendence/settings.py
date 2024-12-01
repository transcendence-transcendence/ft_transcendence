"""
Django settings for ft_transcendence project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv
load_dotenv(override=True)  # override=True를 추가하여 강제 재로드

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
APP_SECRET_KEY = config('APP_SECRET_KEY')
APP_EMAIL = config('APP_EMAIL')
SECRET_KEY = config('DJANGO_SECRET_KEY')
LOCAL_HOST_IP = config('LOCAL_HOST_IP')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'main.User'

# Application definition

INSTALLED_APPS = [
	'daphne',
	'main',
	'game',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
]

# REST Framework와 Simple JWT 설정
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # 세션 인증
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT 인증
    ),
    'DEFAULT_RENDERER_CLASSES': (
        # 'rest_framework.renderers.TemplateHTMLRenderer', # 디버깅 용
        'rest_framework.renderers.JSONRenderer',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),  # JWT 만료 시간 설정
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

ASGI_APPLICATION = 'ft_transcendence.asgi.application'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'ft_transcendence.urls'

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

# WSGI_APPLICATION = 'ft_transcendence.wsgi.application'
# ASGI_APPLICATION = 'ft_transcendence.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

LOGIN_REDIRECT_URL = '/'    # 로그인 후 메인 페이지로 이동
LOGOUT_REDIRECT_URL = '/'   # 로그아웃 후 메인 페이지로 이동

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ft_transcendence',      # 생성한 데이터베이스 이름
        'USER': config('POSTGRES_USER'),                # 생성한 PostgreSQL 사용자 이름
        'PASSWORD':  config('POSTGRES_PASSWORD'),        # PostgreSQL 사용자 비밀번호
        'HOST': 'postgres_container',             # 로컬에서 실행 중이므로 localhost 사용
        'PORT': '5432',                  # PostgreSQL 기본 포트
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis_container', 6379)],  # Redis 서버 주소
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = APP_EMAIL  # 이메일 계정
EMAIL_HOST_PASSWORD = APP_SECRET_KEY     # 계정 앱 비밀번호


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # 최소 길이 설정
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_TRUSTED_ORIGINS = [
    f'http://{LOCAL_HOST_IP}',  # HTTPS 요청
    f'https://{LOCAL_HOST_IP}',  # HTTPS 요청
    f'wss://{LOCAL_HOST_IP}',   # WebSocket 요청
]

INSTALLED_APPS += [
    'corsheaders',  # corsheaders 추가
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    *MIDDLEWARE,
]
CORS_ALLOW_HEADERS = [
    'Authorization',
    'X-CSRFToken',
    'Content-Type',
]
# 허용할 CORS 도메인 설정
CORS_ALLOWED_ORIGINS = [
    f"http://{LOCAL_HOST_IP}:8080",  # SPA가 실행되는 도메인
    f"https://{LOCAL_HOST_IP}",
    f"wss://{LOCAL_HOST_IP}",
]
CSRF_TRUSTED_ORIGINS = [
    f'http://{LOCAL_HOST_IP}:8080',
    f'https://{LOCAL_HOST_IP}',
    f'wss://{LOCAL_HOST_IP}',
]
# 추가 옵션 (필요에 따라 설정)
CORS_ALLOW_CREDENTIALS = True  # 쿠키를 포함한 인증 정보를 전달하도록 허용
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
# CORS_ALLOW_ALL_ORIGINS = True
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
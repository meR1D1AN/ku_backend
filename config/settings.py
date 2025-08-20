import os
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from all_fixture.views_fixture import (
    APPLICATION_SETTINGS,
    AUTH_SETTINGS,
    BLOG_SETTINGS,
    CALENDAR_SETTINGS,
    CATEGORY_SETTINGS,
    COMMENTS_SETTINGS,
    DISCOUNT_SETTINGS,
    ENTREPRISE_SETTINGS,
    FLIGHT_SETTINGS,
    GUEST_SETTINGS,
    HOTEL_PHOTO_SETTINGS,
    HOTEL_SETTINGS,
    INSURANCE_SETTINGS,
    LIKES_SETTINGS,
    MAILING_SETTINGS,
    ROOM_PHOTO_SETTINGS,
    ROOM_SETTINGS,
    TAG_SETTINGS,
    THEME_SETTINGS,
    TOUR_SETTINGS,
    TYPE_OF_MEAL_SETTINGS,
    USER_SETTINGS,
    VZHUH_SETTINGS,
    WHAT_ABOUT_SETTINGS,
)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    # Стандартные Django-приложения
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние библиотеки
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Подключаем OAuth-авторизацию (если нужны соцсети)
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.vk",
    "allauth.socialaccount.providers.yandex",
    # Дополнительные библиотеки
    "drf_spectacular",
    "phonenumber_field",
    "django_celery_beat",
    # Наши приложения
    "users",
    "tours",
    "flights",
    "hotels",
    "rooms",
    "applications",
    "guests",
    "insurances",
    "vzhuhs",
    "mailings",
    "promocodes",
    "calendars",
    "blogs",
    # Поддержка CORS
    "corsheaders",
    "rest_framework_simplejwt.token_blacklist",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 🔹 Добавляем сюда (ВАЖНО: перед AuthenticationMiddleware)
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
USE_L10N = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "static", "media")
# Настройки для тестов
if "test" in sys.argv:
    MEDIA_ROOT = tempfile.mkdtemp(prefix="test_media_")

# Ограничение на размер загружаемого файла в 10 мегабайт
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = ["email"]

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "users.serializers.CustomRegisterSerializer",
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.authentication.CookieJWTAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "TIME_FORMAT": "%H:%M:%S",
    "TIME_INPUT_FORMATS": ["%H:%M:%S", "%H:%M"],
}

SIMPLE_JWT = {
    # Жизнь access-токена
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=7),
    # Жизнь refresh-токена
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # Не создавать новый refresh при обновлении access
    "ROTATE_REFRESH_TOKENS": False,
    # Отозвать старый refresh после ротации, если она включена
    "BLACKLIST_AFTER_ROTATION": True,
    # Обновлять поле last_login при входе
    "UPDATE_LAST_LOGIN": True,
    # Алгоритм шифрования JWT
    "ALGORITHM": "HS256",
    # Ключ подписи токена
    "SIGNING_KEY": SECRET_KEY,
    # Публичный ключ (используется при RS алгоритмах)
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    # Тип токена в заголовке Authorization
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Имя заголовка
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    # Поле идентификатора пользователя
    "USER_ID_FIELD": "id",
    # Ключ внутри токена для ID
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    # Тип токена (access/refresh)
    "TOKEN_TYPE_CLAIM": "token_type",
    # JWT ID, используется для blacklist
    "JTI_CLAIM": "jti",
}

LOGIN_ATTEMPTS_LIMIT = 5  # после 5 неверных попыток — бан по ступеням
LOGIN_BAN_STEPS = [
    timedelta(minutes=15),
    timedelta(hours=1),
    timedelta(days=1),
    timedelta(days=7),
]

SPECTACULAR_SETTINGS = {
    "TITLE": "API приложения Куда Угодно",
    "DESCRIPTION": "Полная документация API приложения Куда Угодно",
    "VERSION": "0.3.1",
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TYPESCRIPT_GENERATOR": {"TYPED_PATH_PARAMETERS": True},
    "TAGS": [
        AUTH_SETTINGS,
        USER_SETTINGS,
        ENTREPRISE_SETTINGS,
        HOTEL_SETTINGS,
        HOTEL_PHOTO_SETTINGS,
        TYPE_OF_MEAL_SETTINGS,
        ROOM_SETTINGS,
        ROOM_PHOTO_SETTINGS,
        CALENDAR_SETTINGS,
        FLIGHT_SETTINGS,
        TOUR_SETTINGS,
        GUEST_SETTINGS,
        APPLICATION_SETTINGS,
        INSURANCE_SETTINGS,
        VZHUH_SETTINGS,
        WHAT_ABOUT_SETTINGS,
        MAILING_SETTINGS,
        DISCOUNT_SETTINGS,
        BLOG_SETTINGS,
        CATEGORY_SETTINGS,
        TAG_SETTINGS,
        THEME_SETTINGS,
        COMMENTS_SETTINGS,
        LIKES_SETTINGS,
    ],
    "SORT_OPERATIONS": True,
    "SORT_OPERATION_PARAMETERS": False,
    "SWAGGER_UI_SETTINGS": {
        "defaultModelsExpandDepth": -1,
    },
    "ENUM_NAME_OVERRIDES": {
        "MedicalInsuranceEnum": "insurances.models.MedicalInsuranceChoices",
        "NotLeavingInsuranceEnum": "insurances.models.NotLeavingInsuranceChoices",
    },
    "POSTPROCESSING_HOOKS": [
        "all_fixture.spectacular_preorder.reorder_operations_postprocessing",
    ],
}

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CORS_ALLOW_CREDENTIALS = True
# Разрешенные домены для CORS (кросс-доменных запросов)
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Безопасность куки и CSRF (важно при работе с куками и кросс-доменом)
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG  # В проде — True, только по HTTPS
SESSION_COOKIE_SECURE = not DEBUG  # В проде — True, только по HTTPS

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

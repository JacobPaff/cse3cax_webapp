from pathlib import Path
import os

# Environment flags
# These flags are used to configure the behavior of the application during development and testing.
# - TESTING: Enables certain testing modes or features (True indicates testing is enabled).
# - LOCALLY_HOSTED: Specifies if the application is running locally or in a production environment (False means it's hosted externally).
# - LOCAL_DB: Determines whether to use a local SQLite database (True) or a remote PostgreSQL database (False).
TESTING = True
LOCALLY_HOSTED = True
LOCAL_DB = True

# Base directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = "django-insecure-%lcu#c0rmx=&38^v$^x7z*#e+dl586b7z=ea5x$!z4bx=05u_6"
DEBUG = True
ALLOWED_HOSTS = ['*']

# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'core',
    'site_admin',
    'manager',
    'lecturer',
    'crispy_forms',
    'crispy_bootstrap4',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Middleware configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL configuration
ROOT_URLCONF = "cse3cax_webapp.urls"

# Template settings
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

# WSGI application
WSGI_APPLICATION = "cse3cax_webapp.wsgi.application"

# Database configuration
if LOCAL_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'cse3cax_webapp',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': '3.106.202.172',
            'PORT': '5432',
        }
    }

# Cognito settings
COGNITO_DOMAIN = 'djangotestunione.auth.ap-southeast-2.amazoncognito.com'
COGNITO_USER_POOL_ID = 'ap-southeast-2_KSJHJw714'
COGNITO_CLIENT_ID = '4vs2np87ek29a3a5r5ertjdjuq'
COGNITO_CLIENT_SECRET = '9n0hkdcp0ihgc3ljlmb3qni6uuuqr198bo0uee96fmm26rn1kct'
COGNITO_REGION = 'ap-southeast-2'

COGNITO_REDIRECT_URI = 'http://localhost:8000/cognito_callback/' if LOCALLY_HOSTED else 'https://rostering.paff.me/cognito_callback/'

# Custom user model
AUTH_USER_MODEL = 'core.UserProfile'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'cse3cax_webapp.backends.CognitoBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

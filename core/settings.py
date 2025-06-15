
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--)z)2xdmln!p*8!uhd2q+$jgu!$cqj^j+x3^wa^u%f&em@fpg='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

# Application definition

INSTALLED_APPS = [
     # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # <-- REQUERIDO POR ALLAUTH

    # Mis Apps
    'core',
    'users',
    'tasks',
    'theme',
    'tailwind',
    'widget_tweaks',
    # Apps de Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # <-- El proveedor para Google
]

TAILWIND_APP_NAME = 'theme'

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # --- Añadir esta línea ---
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# Configuración de Backends de Autenticación (Esto se queda igual)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Requerido por django.contrib.sites (Esto se queda igual)
SITE_ID = 1


# --- INICIA LA CONFIGURACIÓN MODERNA DE DJANGO-ALLAUTH ---

# Le dice a allauth que use nuestras reglas personalizadas para crear usuarios.
ACCOUNT_ADAPTER = 'users.adapter.CustomAccountAdapter'

# Le decimos a allauth que nuestro CustomUser no tiene campo 'username'.
# Esta es la línea clave que elimina las advertencias.
ACCOUNT_USER_MODEL_USERNAME_FIELD = None


# El método de login será exclusivamente a través de email.
ACCOUNT_LOGIN_METHODS = {'email'}

# El email es obligatorio y debe ser verificado.
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- EXPERIENCIA DE USUARIO ---
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True


# --- PROVEEDORES SOCIALES (Esto se queda igual) ---
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
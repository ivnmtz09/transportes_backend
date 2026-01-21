from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# ==============================================================================
# GDAL CONFIGURATION FOR WINDOWS (FIXED FOR PYTHON 3.13)
# ==============================================================================
if os.name == 'nt':
    # Ruta raíz detectada
    OSGEO4W_ROOT = r'C:\Users\ivanj\AppData\Local\Programs\OSGeo4W'
    OSGEO4W_BIN = os.path.join(OSGEO4W_ROOT, 'bin')
    
    if os.path.isdir(OSGEO4W_BIN):
        # 1. ESENCIAL: Agregar el directorio al PATH de búsqueda de DLLs de Python
        os.add_dll_directory(OSGEO4W_BIN)
        
        # 2. Configurar variables de entorno del sistema
        os.environ['PATH'] = OSGEO4W_BIN + os.pathsep + os.environ.get('PATH', '')
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W_ROOT, 'apps', 'gdal', 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'apps', 'proj', 'share', 'proj')
        
        # 3. Definir rutas exactas para GeoDjango
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'gdal312.dll')
        GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'geos_c.dll')

# ==============================================================================
# CORE SETTINGS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')

# ==============================================================================
# SECURITY WARNING: keep the secret key used in production secret!
# ==============================================================================
SECRET_KEY = os.getenv('SECRET_KEY')


if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env file")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allow connections from local network for mobile testing
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,192.168.1.4').split(',')

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',  # PostGIS support
    
    # Third-Party Apps - CORS
    'corsheaders',
    
    # Third-Party Apps - REST Framework
    'rest_framework',
    'rest_framework.authtoken',
    
    # Third-Party Apps - Authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'dj_rest_auth',
    'dj_rest_auth.registration',

    # Project Apps
    'apps.accounts',
    'apps.administration',
    'apps.clients',
    'apps.drivers',
    'apps.fares',
    'apps.notifications',
    'apps.payments',
    'apps.ratings',
    'apps.support',
    'apps.trips',
    'apps.vehicles',
    'apps.chat',
]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'driver_gaitan_db'),
        'USER': os.getenv('DB_USER', 'gaitan_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', '12345'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5433'),
    }
}

# ==============================================================================
# CORS CONFIGURATION (for mobile app integration)
# ==============================================================================

# Allow requests from mobile devices on local network
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.1.4:8000",
    # Add your mobile device IP if needed
]

# Allow credentials (cookies, authorization headers, etc.)
CORS_ALLOW_CREDENTIALS = True

# Allow all methods for development
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow necessary headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ==============================================================================
# AUTHENTICATION & AUTHORIZATION
# ==============================================================================

AUTH_USER_MODEL = 'accounts.User'

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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ==============================================================================
# REST FRAMEWORK & JWT CONFIGURATION
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# ==============================================================================
# SOCIAL AUTHENTICATION (GOOGLE OAUTH)
# ==============================================================================

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''), # Si está vacío en el .env, no rompe
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

REST_USE_JWT = True
JWT_AUTH_COOKIE = 'auth-token'

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# ==============================================================================
# STATIC & MEDIA FILES
# ==============================================================================

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# ALLAUTH & ACCOUNT CONFIGURATION
# ==============================================================================

# Evita que allauth intente enviar correos de verificación (puedes activarlo luego)
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = True

# Esto es clave: Evita que pida un formulario de registro extra si el email ya existe o es nuevo
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

# Forzar el login directo si el email coincide con uno existente
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username' # O None si no usas username

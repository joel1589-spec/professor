from pathlib import Path
import os
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass  # python-dotenv non installe, variables systeme utilisees

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Sécurité ──────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me-en-production')
DEBUG = os.getenv('DEBUG', '1') == '1'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'professor_market.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'store.context_processors.site_settings',
    ]},
}]
WSGI_APPLICATION = 'professor_market.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lome'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = []
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# ── FedaPay ───────────────────────────────────────────────────────────────
# Les clés sont lues depuis les variables d'environnement.
# Crée un fichier .env à la racine du projet avec :
#   FEDAPAY_SECRET_KEY=sk_sandbox_...
#   FEDAPAY_PUBLIC_KEY=pk_sandbox_...
#   FEDAPAY_ENVIRONMENT=sandbox
#
# Récupère tes clés sur https://sandbox.fedapay.com → API Keys
FEDAPAY_SECRET_KEY  = os.getenv('FEDAPAY_SECRET_KEY',  '')  # sk_sandbox_...
FEDAPAY_PUBLIC_KEY  = os.getenv('FEDAPAY_PUBLIC_KEY',  '')  # pk_sandbox_...
# 'sandbox' pour les tests, 'production' pour le vrai paiement
FEDAPAY_ENVIRONMENT = os.getenv('FEDAPAY_ENVIRONMENT', 'sandbox')

FEDAPAY_API_BASE = {
    'sandbox':    'https://sandbox-api.fedapay.com/v1',
    'production': 'https://api.fedapay.com/v1',
}

PAYMENT_DEMO_KEYS = {
    'MOBILE_MONEY_MERCHANT': 'DEMO-MOMO-ESTINO-001',
    'PAYPAL_CLIENT_ID':      'demo_paypal_client_id_replace_me',
    'STRIPE_PUBLIC_KEY':     'pk_test_replace_me',
    'STRIPE_SECRET_KEY':     'sk_test_replace_me',
}

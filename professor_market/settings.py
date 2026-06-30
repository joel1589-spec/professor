from pathlib import Path
import os
import dj_database_url

# ------------------- Base directory -------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------- Variables obligatoires ---------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable d'environnement SECRET_KEY est obligatoire.")

DEBUG = os.getenv("DEBUG", "0") == "1"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "")
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]
else:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = []
csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in csrf_origins.split(",") if u.strip()]
if not any(".onrender.com" in o for o in CSRF_TRUSTED_ORIGINS):
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")

# -------------- Base de données (PostgreSQL) --------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL est obligatoire (Neon PostgreSQL).")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# -------------- Applications et middlewares --------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 🆕 Cloudinary
    "cloudinary",
    "cloudinary_storage",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "professor_market.urls"

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
                "store.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "professor_market.wsgi.application"

# -------------- Internationalisation --------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = True
USE_TZ = True

# -------------- Fichiers statiques et médias --------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# MEDIA_URL doit toujours être défini, même en production (utile pour le fallback
# et pour éviter que Django retombe sur une URL relative vide)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 🆕 Configuration de Cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configuration Cloudinary avec les variables d'environnement
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Initialisation de Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# Django 4.2+/5.x utilise STORAGES (DEFAULT_FILE_STORAGE et STATICFILES_STORAGE
# sont obsolètes et ne sont plus fiables). On définit donc explicitement STORAGES.
# En production (DEBUG=False) : Cloudinary pour les médias, Whitenoise pour le static.
# En développement (DEBUG=True) : stockage local classique pour tout.
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------- Sécurité --------------
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

# -------------- Fedapay --------------
FEDAPAY_SECRET_KEY = os.getenv("FEDAPAY_SECRET_KEY")
FEDAPAY_PUBLIC_KEY = os.getenv("FEDAPAY_PUBLIC_KEY")
FEDAPAY_ENVIRONMENT = os.getenv("FEDAPAY_ENVIRONMENT")

if not (FEDAPAY_SECRET_KEY and FEDAPAY_PUBLIC_KEY and FEDAPAY_ENVIRONMENT):
    raise ValueError(
        "Les variables FEDAPAY_SECRET_KEY, FEDAPAY_PUBLIC_KEY et "
        "FEDAPAY_ENVIRONMENT doivent être définies."
    )

FEDAPAY_API_BASE = {
    "sandbox": "https://sandbox-api.fedapay.com/v1",
    "production": "https://api.fedapay.com/v1",
}

if FEDAPAY_ENVIRONMENT not in FEDAPAY_API_BASE:
    raise ValueError(
        f"FEDAPAY_ENVIRONMENT doit être 'sandbox' ou 'production', reçu '{FEDAPAY_ENVIRONMENT}'"
    )
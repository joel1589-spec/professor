from pathlib import Path
import os
import dj_database_url

# ------------------- Base directory -------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------- Variables obligatoires ---------------
# Toutes ces variables DOIVENT être définies dans l'environnement (Render)
# Aucune valeur par défaut, sauf pour DEBUG (on peut tolérer une valeur par défaut pour le dev local)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable d'environnement SECRET_KEY est obligatoire.")

DEBUG = os.getenv("DEBUG", "0") == "1"   # "1" pour activer, par défaut False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "")
if not ALLOWED_HOSTS:
    # Si vraiment rien, on met une liste minimaliste (mais Render doit fournir cette variable)
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]
else:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(",") if h.strip()]

# CSRF_TRUSTED_ORIGINS – on construit à partir d'une variable, on peut aussi en mettre par défaut
CSRF_TRUSTED_ORIGINS = []
csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in csrf_origins.split(",") if u.strip()]
# On ajoute toujours .onrender.com pour Render (mais on peut l'inclure dans la variable)
if not any(".onrender.com" in o for o in CSRF_TRUSTED_ORIGINS):
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")

# -------------- Base de données (PostgreSQL uniquement) --------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable d'environnement DATABASE_URL est obligatoire (Neon PostgreSQL).")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,   # en production, on force SSL
    )
}

# -------------- Applications et middlewares (inchangés) --------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------- Sécurité (toujours adaptée à la production) --------------
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
X_FRAME_OPTIONS = "DENY"

# -------------- Fedapay (Tout vient des variables d'env) --------------
FEDAPAY_SECRET_KEY = os.getenv("FEDAPAY_SECRET_KEY")
FEDAPAY_PUBLIC_KEY = os.getenv("FEDAPAY_PUBLIC_KEY")
FEDAPAY_ENVIRONMENT = os.getenv("FEDAPAY_ENVIRONMENT")

# On vérifie que ces trois sont bien définies (production obligatoire)
if not (FEDAPAY_SECRET_KEY and FEDAPAY_PUBLIC_KEY and FEDAPAY_ENVIRONMENT):
    raise ValueError(
        "Les variables FEDAPAY_SECRET_KEY, FEDAPAY_PUBLIC_KEY et "
        "FEDAPAY_ENVIRONMENT doivent être définies."
    )

FEDAPAY_API_BASE = {
    "sandbox": "https://sandbox-api.fedapay.com/v1",
    "production": "https://api.fedapay.com/v1",
}

# On peut éventuellement valider que l'environnement est correct
if FEDAPAY_ENVIRONMENT not in FEDAPAY_API_BASE:
    raise ValueError(
        f"FEDAPAY_ENVIRONMENT doit être 'sandbox' ou 'production', reçu '{FEDAPAY_ENVIRONMENT}'"
    )

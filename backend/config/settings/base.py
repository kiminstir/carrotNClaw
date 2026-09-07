from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
REPO_DIR = BASE_DIR.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(REPO_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])

INSTALLED_APPS = [
    "apps.pages",
    "apps.navigation",
    "apps.music",
    "apps.api",
    "wagtail.contrib.settings",
    "wagtail.api.v2",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail_headless_preview",
    "modelcluster",
    "taggit",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": env.db("DATABASE_URL")}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Wagtail -----------------------------------------------------------------

WAGTAIL_SITE_NAME = "Carrot&Claw"
BACKEND_PUBLIC_URL = env("BACKEND_PUBLIC_URL", default="http://localhost:8000")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:5173")

WAGTAILADMIN_BASE_URL = BACKEND_PUBLIC_URL
WAGTAILAPI_BASE_URL = BACKEND_PUBLIC_URL
WAGTAILAPI_LIMIT_MAX = 50
WAGTAILAPI_RICH_TEXT_FORMAT = "html"

WAGTAILDOCS_SERVE_METHOD = "direct"
WAGTAILDOCS_EXTENSIONS = ["mp3", "ogg", "m4a", "wav", "pdf"]
WAGTAILDOCS_MAX_UPLOAD_SIZE = 30 * 1024 * 1024
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 15 * 1024 * 1024

WAGTAIL_HEADLESS_PREVIEW = {
    "CLIENT_URLS": {"default": f"{FRONTEND_URL}/preview"},
    "SERVE_BASE_URL": FRONTEND_URL,
    "REDIRECT_ON_PREVIEW": True,
    "ENFORCE_TRAILING_SLASH": True,
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

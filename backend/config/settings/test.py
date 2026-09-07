from .dev import *  # noqa: F403

MEDIA_ROOT = BASE_DIR / ".test-media"  # noqa: F405
BACKEND_PUBLIC_URL = "http://testserver"
WAGTAILADMIN_BASE_URL = BACKEND_PUBLIC_URL
WAGTAILAPI_BASE_URL = BACKEND_PUBLIC_URL
FRONTEND_URL = "http://frontend.test"
WAGTAIL_HEADLESS_PREVIEW["CLIENT_URLS"] = {"default": f"{FRONTEND_URL}/preview"}  # noqa: F405
WAGTAIL_HEADLESS_PREVIEW["SERVE_BASE_URL"] = FRONTEND_URL  # noqa: F405
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

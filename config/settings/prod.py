from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "yumi.loaywaleed.tech",
]

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://loaywaleed.tech",
    "http://localhost:8000",
    "http://locahost:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]

# Cookie Security Settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = ".loaywaleed.tech"
SESSION_COOKIE_DOMAIN = ".loaywaleed.tech"
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
# rest auth
REST_AUTH.update(
    {
        "JWT_AUTH_COOKIE_DOMAIN": ".loaywaleed.tech",
        "JWT_AUTH_SECURE": True,
        "JWT_AUTH_SAMESITE": "None",
    }
)

# rate limiting
REST_FRAMEWORK.update(
    {
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "anon": "100/day",
            "user": "1000/day",
        },
    }
)

# Security Headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

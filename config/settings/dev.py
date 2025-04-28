from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# Cookie settings (dev)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# JWT Cookie settings (dev)
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = False

# # Logging
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "INFO",
#         },
#         "django.db.backends": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": False,
#         },
#     },
# }

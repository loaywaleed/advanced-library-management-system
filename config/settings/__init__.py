from .base import *

if os.getenv("DJANGO_ENV") == "production":
    from .prod import *
else:
    from .dev import *

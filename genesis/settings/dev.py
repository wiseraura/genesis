from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-4n8@c0ho7j9i9_w^3ks3nrznqgqktq2q(@u38k7lhdpb*d)$%4"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# try:
#     from .local import *
# except ImportError:
#     pass

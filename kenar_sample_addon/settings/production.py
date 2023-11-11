import os
from django.core.management.commands.runserver import Command as runserver
from .base import HOST

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ["DATABASE_NAME"],
        'USER': os.environ["DATABASE_USER"],
        'PASSWORD': os.environ["DATABASE_PWD"],
        'HOST': os.environ["DATABASE_HOST"],
        'PORT': int(os.environ["DATABASE_PORT"]),
    }
}

ALLOWED_HOSTS = [HOST, ]

runserver.default_port = os.environ.get("SERVER_PORT", "80")
runserver.default_addr = os.environ.get("SERVER_ADDR", "0.0.0.0")


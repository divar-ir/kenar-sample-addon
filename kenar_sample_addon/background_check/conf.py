import os

from appconf import AppConf
from django.conf import settings


class BackgroundCheckConf(AppConf):
    KENAR_API_KEY = os.environ.get("BACKGROUND_CHECK_KENAR_API_KEY", "api-key")
    KENAR_APP_SLUG = os.environ.get("BACKGROUND_CHECK_KENAR_APP_SLUG", "divar-background-check")
    KENAR_OAUTH_SECRET = os.environ.get("BACKGROUND_CHECK_KENAR_OAUTH_SECRET", None)

    ESTL_USERNAME = os.environ.get("ESTL_USERNAME", 'your-username')
    ESTL_PASSWORD = os.environ.get("ESTL_PWD", 'your-password')
    ESTL_WSDL_URL = os.environ.get("ESTL_WSDL_URL", 'your-url')
    ESTL_WSDL_TERMINAL_ID = os.environ.get("ESTL_WSDL_TERMINAL_ID", 'your-terminal-id')
    ESTL_WSDL_PASSWORD = os.environ.get("ESTL_WSDL_PWD", 'your-password')

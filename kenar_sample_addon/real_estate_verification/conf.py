import os

from appconf import AppConf

from django.conf import settings


class RealEstateVerificationConf(AppConf):
    KENAR_API_KEY = os.environ.get("REAL_ESTATE_VERIFICATION_KENAR_API_KEY", "api-key")
    KENAR_APP_SLUG = os.environ.get("REAL_ESTATE_VERIFICATION_KENAR_APP_SLUG", "verification-addon")
    KENAR_OAUTH_SECRET = os.environ.get("REAL_ESTATE_VERIFICATION_KENAR_OAUTH_SECRET", None)

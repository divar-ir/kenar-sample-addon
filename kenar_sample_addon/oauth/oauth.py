import base64
import random
import string
from datetime import datetime

from caseconverter import macrocase
from cryptography.fernet import Fernet
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from kenar_sample_addon.kenar.clients.finder import finder_client
from kenar_sample_addon.kenar.clients.oauth import oauth_client
from kenar_sample_addon.oauth.models import OAuth, PermissionTypes

STATE_SALT_LEN = 10

fernet = Fernet(settings.ENCRYPTION_KEY)


def get_oauth(code, app_name, *args, **kwargs) -> OAuth:
    token = oauth_client.get_token(
        code=code,
        app_slug=_get_app_slug(app_name),
        oauth_api_key=_get_oauth_api_key(app_name)
    )

    access_token, refresh_token = token['access_token'], token['refresh_token']
    expires = datetime.fromtimestamp(int(token['expires']), timezone.utc)

    return OAuth(access_token=access_token, refresh_token=refresh_token,
                 expires=expires, *args, **kwargs)


# noinspection PyTypeChecker,PyNoneFunctionAssignment
def create_redirect_link(request, scopes, callback_view, app_name: str, state_data: str = "") -> str:
    if request.user.is_authenticated:
        OAuth.objects.filter(user=request.user).delete()

    salt = ''.join(random.choices(string.ascii_letters, k=STATE_SALT_LEN))

    if state_data != "":
        encryption = fernet.encrypt(f"{state_data}\n{salt}".encode())
        state = base64.urlsafe_b64encode(
            encryption
        ).decode()
    else:
        state = salt

    oauth_url = oauth_client.create_redirect_link(
        app_slug=_get_app_slug(app_name),
        redirect_uri=settings.HOST_PREFIX + settings.HOST + reverse('oauth:callback'),
        scopes=scopes,
        state=state
    )

    request.session[settings.OAUTH_INFO_SESSION_KEY] = {
        "state": state,
        "scopes": scopes,
        "callback_view": callback_view,
        "oauth_url": oauth_url,
        "app_name": app_name,
    }

    return oauth_url


def create_phone_scope() -> str:
    return PermissionTypes.USER_PHONE.name


def create_sticky_addon_scope() -> str:
    return PermissionTypes.ADDON_STICKY_CREATE.name


def create_approved_addon_scope(token: str) -> str:
    return f"{PermissionTypes.ADDON_USER_APPROVED.name}__{token}"


def extract_state_data(state: str) -> str:
    decrypted_state = fernet.decrypt(base64.urlsafe_b64decode(state.encode())).decode()
    if '\n' not in decrypted_state:
        return ""

    return decrypted_state[:decrypted_state.index('\n')]


def get_phone_numbers(app_name, access_token):
    return finder_client.get_user(_get_oauth_api_key(app_name), access_token)["phone_numbers"]


def _get_oauth_api_key(app_name):
    api_key = getattr(settings, f"{macrocase(app_name)}_KENAR_OAUTH_SECRET", None)
    if api_key:
        return api_key

    return getattr(settings, f"{macrocase(app_name)}_KENAR_API_KEY")


def _get_app_slug(app_name):
    return getattr(settings, f"{macrocase(app_name)}_KENAR_APP_SLUG")

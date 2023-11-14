import logging
from typing import List, Union, Tuple

import pybreaker
import requests
from requests import JSONDecodeError
from requests.models import PreparedRequest

from kenar_sample_addon.kenar.utils.proxy import DivarHTTPProxy

logger = logging.getLogger(__name__)


class OAuthException(Exception):
    pass


class OAuthClient(DivarHTTPProxy):
    _REDIRECT_BASE_URI = 'https://open-platform-redirect.divar.ir/oauth'
    _OAUTH_GET_TOKEN_ENDPOINT = 'https://api.divar.ir/v1/open-platform/oauth/access_token'

    def create_redirect_link(
            self,
            app_slug: str,
            scopes: Union[List[str], Tuple[str]],
            state: str,
            redirect_uri: str,
    ):
        params = {
            'client_id': app_slug,
            'scope': ' '.join(scopes),
            'state': state,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
        }
        req = PreparedRequest()
        req.prepare_url(self._REDIRECT_BASE_URI, params)
        return req.url

    def get_token(self, code, app_slug, oauth_api_key):
        headers = {
            'api_key': oauth_api_key
        }
        data = {
            'code': code,
            'client_id': app_slug,
            'client_secret': oauth_api_key,
            'grant_type': 'authorization_code',
        }
        try:
            resp = self._post(
                self._OAUTH_GET_TOKEN_ENDPOINT,
                json=data,
                headers=headers,
            )
            resp.raise_for_status()
        except JSONDecodeError as e:
            logger.exception('Unable to parse response as json', e)
            raise OAuthException("decode error")
        except (requests.RequestException, pybreaker.CircuitBreakerError) as e:
            logger.exception("request failed", e)
            raise OAuthException("request failed")
        return resp.json()


oauth_client = OAuthClient.get_instance(max_retry=3)

import logging
from http import HTTPStatus
from typing import Optional

import pybreaker
import requests
from requests import JSONDecodeError

from kenar_sample_addon.kenar.utils.proxy import DivarHTTPProxy
from kenar_sample_addon.kenar.models.post import Post

logger = logging.getLogger(__name__)


class FinderException(Exception):
    pass


class FinderClient(DivarHTTPProxy):
    _GET_POST_ENDPOINT = 'https://api.divar.ir/v1/open-platform/finder/post/{token}'
    _GET_USER_ENDPOINT = 'https://api.divar.ir/v1/open-platform/users'

    def get_post(self, token: str, api_key: str, timeout: int = 5) -> Post:
        try:
            r: requests.Response = self._get(
                url=self._GET_POST_ENDPOINT.format(token=token),
                headers={
                    "x-api-key": api_key,
                },
                timeout=timeout,
            )
            r.raise_for_status()

            return Post(r.json())
        except JSONDecodeError:
            logger.exception('Unable to parse response as json')
            raise FinderException("decode error")
        except (requests.RequestException, pybreaker.CircuitBreakerError) as e:
            logger.exception(e)
            raise FinderException("request failed")

    def does_post_exist(self, token: str, api_key: str, timeout: int = 5) -> bool:
        try:
            r: requests.Response = self._get(
                url=self._GET_POST_ENDPOINT.format(token=token),
                headers={
                    "x-api-key": api_key,
                },
                timeout=timeout,
            )
            if r.status_code == HTTPStatus.NOT_FOUND:
                return False
            if r.status_code == HTTPStatus.OK:
                return True
            r.raise_for_status()
        except JSONDecodeError:
            logger.exception('Unable to parse response as json')
            raise FinderException("decode error")
        except (requests.RequestException, pybreaker.CircuitBreakerError) as e:
            logger.exception(e)
            raise FinderException("request failed")

        logger.error("invalid status code", r.status_code)
        raise FinderException(f"invalid status code {r.status_code}")

    def get_user(self, api_key: str, access_token: Optional[str] = None):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            'x-api-key': api_key,
        }
        if access_token:
            headers['x-access-token'] = access_token

        try:
            resp = self._post(
                self._GET_USER_ENDPOINT,
                json={},
                headers=headers
            )
            resp.raise_for_status()
        except JSONDecodeError as e:
            logger.exception('Unable to parse response as json', e)
            raise FinderException("decode error")
        except (requests.RequestException, pybreaker.CircuitBreakerError) as e:
            logger.exception("request failed", e)
            raise FinderException("request failed")

        return resp.json()


finder_client = FinderClient.get_instance(max_retry=3)

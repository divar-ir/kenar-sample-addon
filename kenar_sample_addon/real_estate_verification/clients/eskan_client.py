import logging
from json import JSONDecodeError

import pybreaker
import requests
from django.conf import settings

from kenar_sample_addon.kenar.utils.proxy import DivarHTTPProxy

logger = logging.getLogger(__name__)


class EskanProxyException(Exception):
    pass


class EskanProxy(DivarHTTPProxy):
    def verify_ownership(self, national_id: str, postal_code: str) -> bool:
        try:
            r: requests.Response = self._post(
                url=f"{settings.AMLAK_ESKAN_URL}api/v1/person/ownership/verify",
                headers={
                    "x-api-key": settings.ESKAN_API_KEY,
                },
                json={
                    "nationalcode": national_id,
                    "postcode": postal_code
                },
                timeout=2,
            )
            r.raise_for_status()
            json_response = r.json()
            is_verified = json_response['isVerified']
        except JSONDecodeError:
            logger.exception('Unable to parse response as json')
            raise EskanProxyException()
        except KeyError as e:
            logger.exception('Unable to parse EskanProxy response', extra={'response': json_response})
            raise EskanProxyException()
        except (requests.RequestException, pybreaker.CircuitBreakerError) as e:
            logger.exception(e)
            raise EskanProxyException()

        return is_verified


eskan_proxy = EskanProxy.get_instance(max_retry=3)

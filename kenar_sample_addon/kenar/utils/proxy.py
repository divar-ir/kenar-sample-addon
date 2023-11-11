from typing import Optional

import requests
import kenar_sample_addon.kenar.utils.requests as kenar_requests
from retry.api import retry_call
import pybreaker

import divar_rpc


class DivarGRPCProxy(object):
    __instance = None
    service_name = None

    def __init__(self, service_name):
        self._service_name = service_name

    def _grpc_call(self, item, *args, **kwargs):
        stub = divar_rpc.get_stub(self._service_name)
        return getattr(stub, item)(*args, **kwargs)

    def __getattr__(self, item):
        def wrapper(*args, **kwargs):
            return self._grpc_call(item, *args, **kwargs)

        return wrapper

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls(cls.service_name)
        return cls.__instance


class DivarHTTPProxy:
    instance = None

    def __init__(
            self,
            max_retry=1,
            circuit_breaker: Optional[pybreaker.CircuitBreaker] = None
    ):
        assert max_retry <= 1 or circuit_breaker is not None

        self.max_retry = max_retry
        self.circuit_breaker = circuit_breaker

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls.instance is None:
            breaker = pybreaker.CircuitBreaker(fail_max=3)
            cls.instance = cls(circuit_breaker=breaker, *args, **kwargs)
        return cls.instance

    def _perform_request(self, method, url, **kwargs):
        if self.circuit_breaker:
            return self.circuit_breaker.call(
                kenar_requests.request, method, url, **kwargs
            )
        return kenar_requests.request(method, url, **kwargs)

    def _post(self, url, data=None, json=None, **kwargs):
        request_args = {'data': data, 'json': json}
        request_args.update(kwargs)

        return retry_call(
            f=self._perform_request,
            fargs=('post', url),
            fkwargs=request_args,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )

    def _get(self, url, **kwargs):
        return retry_call(
            f=self._perform_request,
            fargs=('get', url),
            fkwargs=kwargs,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )

    def _put(self, url, data=None, json=None, **kwargs):
        request_args = {'data': data, 'json': json}
        request_args.update(kwargs)

        return retry_call(
            f=self._perform_request,
            fargs=('put', url),
            fkwargs=request_args,
            exceptions=requests.Timeout,
            tries=self.max_retry,
            backoff=2,
            max_delay=0.01,
        )

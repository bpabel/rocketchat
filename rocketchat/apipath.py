import inspect
import json
import logging
from typing import Optional, Union

import requests

from .errors import RocketChatError
from .rocketchat import RocketChat

LOG = logging.getLogger(__name__)


class APIPath(object):
    """
    Descriptor object for defining RocketChat API calls.
    """

    def __init__(
        self,
        api: "RocketChat",
        path: str,
        method: Union[str, None] = "GET",
        arg_endpoint: bool = False,
        result_key: Optional[str] = None,
        auth: bool = True,
        api_root: str = "/api/v1/",
    ):
        """
        Args:
            api: The Rockchat instance to send the api call to.
            path: API endpoint (e.g. self.users.create)
            method: HTTP method (e.g. GET, POST, DELETE). Defaults to "GET", if
                set to None, it will not be a valid endpoint and will raise an 
                exception if called as one.
            arg_endpoint: If True, this APIPath will accept a single positional 
                argument that will be added to the api path with a preceding 
                slash to create the final endpoint. (e.g. api.settings.get('ARG') -> /settings/ARG
            result_key: A specific key in the returned json object that should 
                be returned instead of the entire json response object.
            auth: Whether this call requires authorization or not.
            api_root: Specify an alternate root path for the api endpoints.
        """
        self._api = api
        self._path = path
        self._method = method
        self._arg_endpoint = arg_endpoint
        self._result_key = result_key
        self._auth = auth
        self._api_root = api_root

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, repr(self._path))

    def __repr__(self):
        args = inspect.getargspec(self.__init__).args[1:]
        attrs = ["{}={}".format(arg, repr(getattr(self, "_" + arg))) for arg in args]
        return "{}({})".format(self.__class__.__name__, ", ".join(attrs))

    def _url(self):
        return self._api.url + self._api_root + self._path

    def __call__(self, *args, **kwargs):
        if self._method is None:
            raise ValueError("Not a valid endpoint: {}".format(self._path))

        if self._method == "GET":
            params = kwargs
            data = None
        else:
            params = None
            data = json.dumps(kwargs)

        url = self._url()
        if self._arg_endpoint:
            url += "/{}".format(args[0])

        request_kwargs = {}
        if self._auth:
            request_kwargs["headers"] = self._api.auth_header()

        r = requests.request(
            method=self._method, url=url, params=params, data=data, **request_kwargs,
        )
        try:
            result = r.json()
        except Exception:
            LOG.debug(
                "Error Response:\n"
                "  Status: {}\n"
                "  Text: {}\n".format(r.status_code, r.text)
            )
            raise

        if "error" in result:
            raise RocketChatError(result["errorType"], result["error"])

        if self._result_key is not None:
            result = result[self._result_key]
        return result

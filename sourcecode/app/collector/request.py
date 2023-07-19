"""Communicator to send the request to external sources like Rest APIs."""

from typing import Any, Dict

from requests.models import Response
from sac_requests.constants.general import (
    AUTH_TYPE,
    AUTHORIZATION,
    BEARER_TOKEN,
    HEADERS,
)
from sac_requests.exceptions.base import HttpRequestError
from sac_requests.wrapper import HttpRequestWrapper


class Request:
    """Prepare request to be sent to REST API."""

    def __init__(
        self, url: str, auth: Any = None, token: Any = None, **kwargs: Dict[str, Any]
    ) -> None:
        """Initialise the requests object.

        Either authentication credentials or token should be supplied.

        :param url: URL to which to send the request
        :type url: str
        :param auth: Authentication credentials, defaults to None
        :type auth: Any, optional
        :param token: Token for athentication, defaults to None
        :type token: Any (str), optional
        """
        # It's a bearer token request
        self._token = token
        self._auth_type = auth

        # Collect request headers
        kwargs[HEADERS] = self._headers()

        # Create Httprequest wrapper object
        self._request = HttpRequestWrapper(url, **kwargs)

    def __str__(self) -> str:
        """Get string representation of the Request object.

        :return: Request object
        :rtype: str
        """
        return f"<Request url={self._auth_type}>"

    def __repr__(self) -> str:
        """Get raw representation of the Request object.

        :return: request object
        :rtype: str
        """
        return f"<Request url={self._auth_type}>"

    def _headers(self) -> Dict[str, Any]:
        """Create headers for the request.

        :return: Headers for the request
        :rtype: Dict[str, Any]
        """
        header = {"Content-Type": "application/json", AUTH_TYPE: self._auth_type}

        if self._auth_type == BEARER_TOKEN:
            header[AUTHORIZATION] = f"Bearer {self._token}"

        return header

    def send(
        self,
        method: str,
        endpoint: str,
        data: Any = None,
        params: Any = None,
        **kwargs: Dict[str, Any],
    ) -> Response:
        """Send the request to the endpoint.

        :param method: Request method type
        :type method: str
        :param endpoint: Enpoint
        :type endpoint: str
        :param data: Data to be sent as a payload, defaults to None
        :type data: Any, optional
        :param params: Params to be sent in query parameters, defaults to None
        :type params: Any, optional
        :return: Response received from the endpoint
        :rtype: Response
        """
        response = Response()

        if not kwargs.get(HEADERS, None):
            # Add empty headers if they are not supplied
            kwargs[HEADERS] = {}

        try:
            response = self._request.send(
                method, endpoint, data=data, params=params, **kwargs
            )
        except ValueError:
            # There is an error received from the API
            response.status_code = 400
        except HttpRequestError as err:
            # There is an error received from the API
            response.status_code = err.errcode
            response._content = str(err)

        return response

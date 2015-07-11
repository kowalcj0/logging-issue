import base64
import httplib
import json
import logging
import requests


class ResponseWrapper(object):

    def __init__(self, response):
        self._response = response

    def __getitem__(self, item):
        return self._response[item]

    def __getattr__(self, item):
        return getattr(self._response, item)

    def __repr__(self):
        return repr(self._response)

    # Assertion helpers

    def _assert_status(self, expected_status):
        error_msg = "Expecting HTTP status code {} but got {}".format(expected_status, self.status_code)
        if self.headers['Content-Type'] == 'application/json':
            try:
                error_msg += "\nResponse:\n%s".format(self.pretty_json())
            except ValueError:
                # Sometimes we get an empty body for JSON responses
                pass
        assert self.status_code == expected_status, error_msg

    def assert_status_ok(self):
        self._assert_status(httplib.OK)

    def assert_status_not_found(self):
        self._assert_status(httplib.NOT_FOUND)

    def assert_status_unsupported_media_type(self):
        self._assert_status(httplib.UNSUPPORTED_MEDIA_TYPE)

    def assert_status_forbidden(self):
        self._assert_status(httplib.FORBIDDEN)

    def assert_status_method_not_allowed(self):
        self._assert_status(httplib.METHOD_NOT_ALLOWED)

    def assert_status_bad_request(self):
        self._assert_status(httplib.BAD_REQUEST)

    def assert_status_created(self):
        self._assert_status(httplib.CREATED)

    def assert_status_no_content(self):
        self._assert_status(httplib.NO_CONTENT)

    def assert_allowed_methods(self, *methods):
        return methods == self.allowed_methods

    def assert_data_fields(self, *fields):
        assert self.data_fields == set(fields)

    def assert_data_list_fields(self, *fields):
        assert len(self.data) > 0
        assert self.data_list_fields == set(fields)

    def assert_has_error_fields(self):
        """
        Check if JSON response has correct fields for an error response
        """
        fields = set(self.json().keys())
        assert fields == set(['message', 'description', 'errors'])

    @property
    def allowed_methods(self):
        return set(self.headers['Allow'].split(","))

    @property
    def data(self):
        return self.json()['data']

    @property
    def metadata(self):
        return self.json()['metadata']

    @property
    def data_fields(self):
        return set(self.data.keys())

    @property
    def data_list_fields(self):
        return set(self.data[0].keys())

    def pretty_json(self):
        return json.dumps(self.json(), indent=4)

    def pprint(self):
        print(self.pretty_json())


class Client(object):

    session_token = None

    def __init__(self, platform_url, access_key=None, secret_key=None):
        self.PLATFORM_URL = platform_url
        self._session = requests.Session()

    def set_content_type_as_url_encoded(self):
        self.set_content_type_header('application/x-www-form-urlencoded')

    def set_content_type_as_json(self):
        self.set_content_type_header('application/json')

    def set_content_type_as_xml(self):
        self.set_content_type_header('application/xml')

    def set_content_type_header(self, content_type):
        self._session.headers['Content-Type'] = content_type

    def set_accept_type_as_json(self):
        self.set_accept_type_header('application/json')

    def set_accept_type_as_xml(self):
        self.set_accept_type_header('application/xml')

    def set_accept_type_header(self, accept_type):
        self._session.headers['Accept'] = accept_type

    def url(self, path):
        return self.PLATFORM_URL + path

    def request(self, method, path, **kwargs):
        payload = kwargs.pop('payload', None)
        if payload:
            kwargs['data'] = json.dumps(payload)
        r = self._session.request(method, self.url(path), **kwargs)
        return ResponseWrapper(r)

    def head(self, path, **kwargs):
        self.set_content_type_as_url_encoded()
        return self.request('HEAD', path, **kwargs)

    def options(self, path, **kwargs):
        self.set_content_type_as_url_encoded()
        return self.request('OPTIONS', path, **kwargs)

    def get(self, path, **kwargs):
        self.set_content_type_as_url_encoded()
        return self.request('GET', path, **kwargs)

    def post(self, path, payload=None, **kwargs):
        self.set_content_type_as_json()
        if payload is None:
            payload = {}
        return self.request('POST', path, payload=payload, **kwargs)

    def patch(self, path, payload, **kwargs):
        self.set_content_type_as_json()
        return self.request('PATCH', path, payload=payload, **kwargs)

    def delete(self, path, **kwargs):
        self.set_content_type_as_url_encoded()
        return self.request('DELETE', path, **kwargs)

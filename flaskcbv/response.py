from flask import stream_with_context, Response as FlaskResponse
from flask import make_response
from flask import redirect
try: from flaskcbv.conf import settings
except: settings = None


class Response(object):
    """Wraps the data to be returned to the client.

    Accepts plain strings, callables, or generators.  Callables are
    invoked at render time; generators are streamed via
    ``flask.stream_with_context``.

    Args:
        data (str | callable | generator): Response body.
    """

    def __init__(self, data="", **kwargs):
        self.data = data
        self.custom_headers = {}

    def _render(self):
        gen_ = self.data
        if gen_.__class__.__name__ == 'function':
            gen_ = self.data()
        if gen_.__class__.__name__ == 'generator':
            return FlaskResponse(stream_with_context(gen_))

        return make_response(gen_)

    def add_header(self, name, value):
        """Queue a custom header to include in the response.

        Args:
            name (str): Header name.
            value (str): Header value.
        """
        self.custom_headers[name] = value
    

    def get_headers(self, **kwargs):
        headers = {}
        if settings is not None:
            headers.update(settings.DEFAULT_HEADERS)
        headers.update(self.custom_headers)
        return headers
        


    def render(self, headers=None):
        """Build and return the final ``flask.Response`` object.

        Merges ``DEFAULT_HEADERS`` from settings, custom headers added
        via ``add_header()``, and any headers passed as *headers*.

        Args:
            headers (dict): Additional headers, typically from
                ``View.get_headers()``.

        Returns:
            flask.Response: The HTTP response ready for Flask.
        """
        if headers is None:
            headers = {}
        r = self._render()
        headers.update(self.get_headers())
        for header in headers:
            r.headers[header] = headers[header]
        return r

        


class ResponseRedirect(Response):
    """Response that issues an HTTP redirect.

    Args:
        url (str): Redirect target URL.
        code (int): HTTP status code. Defaults to 302.
    """

    def __init__(self, url, code=302, **kwargs):
        self.url = url
        self.code = code
        super(ResponseRedirect, self).__init__(**kwargs)

    def render(self, *args, **kwargs):
        r = redirect(self.url, code=self.code)
        headers = self.get_headers()
        for header in headers:
            r.headers[header] = headers[header]
        return r



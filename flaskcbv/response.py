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
        status (int): HTTP status code. None keeps what Flask chooses (200).
    """

    ## Class default: a subclass whose __init__ skips super() still renders.
    status = None

    def __init__(self, data="", status=None, **kwargs):
        self.data = data
        self.status = status
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
        if self.status is not None:
            r.status_code = self.status
        headers.update(self.get_headers())
        for header in headers:
            r.headers[header] = headers[header]
        return r

        


class ResponseRedirect(Response):
    """Response that issues an HTTP redirect.

    Args:
        url (str): Redirect target URL.
        code (int): HTTP status code. Defaults to 302. ``status=`` is
            accepted too and takes precedence.
    """

    def __init__(self, url, code=302, **kwargs):
        self.url = url
        self.code = code
        super(ResponseRedirect, self).__init__(**kwargs)

    def render(self, *args, **kwargs):
        ## `status`, when given, wins over `code`: both name the same thing.
        r = redirect(self.url, code=self.status if self.status is not None else self.code)
        headers = self.get_headers()
        for header in headers:
            r.headers[header] = headers[header]
        return r


class ResponseNotModified(Response):
    """304 Not Modified: the client's cached copy is still current.

    The body is always empty; werkzeug drops it for 304 anyway. Headers such
    as ``ETag`` and ``Cache-Control`` are added with ``add_header()``.

    Args:
        etag (str): Optional ETag to repeat in the response.
    """

    def __init__(self, etag=None, **kwargs):
        super(ResponseNotModified, self).__init__('', status=304, **kwargs)
        if etag is not None:
            self.add_header('ETag', etag)

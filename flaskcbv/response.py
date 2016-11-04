from flask import stream_with_context, Response as FlaskResponse
from flask import make_response
from flask import redirect
try: from flaskcbv.conf import settings
except: settings = None


class Response(object):
    def __init__(self, data="", **kwargs):
        self.data = data
        self.custom_headers = {}

    def _render(self):
        gen_ = self.data
        if gen_.__class__.__name__ == 'function':
            gen_ = self.data()
        if gen_.__class__.__name__ == 'generator':
            return FlaskResponse(stream_with_context(gen_))
            
        return make_response(self.data)

    def add_header(self, name, value):
        self.custom_headers[name] = value
    

    def get_headers(self, **kwargs):
        headers = {}
        if settings is not None:
            headers.update(settings.DEFAULT_HEADERS)
        headers.update(self.custom_headers)
        return headers
        


    def render(self, headers={}):
        r = self._render()
        headers.update(self.get_headers())
        for header in headers:
            r.headers[header] = headers[header]
        return r

        


class ResponseRedirect(Response):
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



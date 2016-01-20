import werkzeug.exceptions as ex
from flask import abort
from flaskcbv.response import Response
from flaskcbv.conf import settings


from flaskcbv.view.mixins import JSONMixin


class defaultHeadersException(JSONMixin):
    def get_headers(self, *args, **kwargs):
        headers = super(defaultHeadersException, self).get_headers(*args, **kwargs)
        for header in settings.DEFAULT_HEADERS:
            headers.append((header, settings.DEFAULT_HEADERS[header]),)
        return headers


class LoginFailedException(defaultHeadersException, ex.HTTPException):
    code = 403
    description = 'Wrong session!'

    def get_body(self, *args, **kwargs):
        if isinstance(self.description, dict):
            return self.json_error(error='auth_error', **self.description)
        return self.json_error(error='auth_error', details=self.description)


abort.mapping[403] = LoginFailedException


class UnauthorizedException(LoginFailedException):
    code = 401
    description = 'Unauthorized!'

abort.mapping[401] = UnauthorizedException


class RedirectException(defaultHeadersException, ex.HTTPException):
    code = 302
    description = 'Redirect'

    def __init__(self, location, *args, **kwargs):
        self.location = location
        return super(RedirectException, self).__init__(*args, **kwargs)

    def get_headers(self, *args, **kwargs):
        headers = super(RedirectException, self).get_headers(*args, **kwargs)
        headers.append(('Location', self.location),)
        return headers

    def get_body(self, *args, **kwargs):
        if isinstance(self.description, dict):
            return self.json_error(**self.description)
        return self.json_error(location=self.location, details=self.description)


abort.mapping[302] = RedirectException



class NotFoundException(defaultHeadersException, ex.HTTPException):
    code = 404
    description = 'Not Found!'

    def get_body(self, *args, **kwargs):
        if isinstance(self.description, dict):
            return self.json_error(error='not_exist_error', **self.description)
        return self.json_error(error='not_exist_error', details=self.description)


abort.mapping[404] = NotFoundException


class BadRequestException(defaultHeadersException, ex.HTTPException):
    code = 400
    description = 'Bad Request'

    def get_body(self, *args, **kwargs):
        if isinstance(self.description, dict):
            return self.json_error(error='bad_request', **self.description)
        return self.json_error(error='bad_request', details=self.description)


abort.mapping[400] = BadRequestException



class InternalServerErrorException(defaultHeadersException, ex.HTTPException):
    code = 500
    description = 'InternalServerError'

    def get_body(self, *args, **kwargs):
        if isinstance(self.description, dict):
            return self.json_error(error='internal_server_error', **self.description)
        return self.json_error(error='internal_server_error', details=self.description)


abort.mapping[500] = InternalServerErrorException


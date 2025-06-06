from flask.wrappers import Request as RequestFlask

class Request(RequestFlask):

    @property
    def is_ajax(self):
        return self.is_xhr

    @property
    def remote_address(self):
        return self.environ.get('HTTP_X_REAL_IP', self.remote_addr)

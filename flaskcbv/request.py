from flask.wrappers import Request as RequestFlask

class Request(RequestFlask):

    @property
    def is_ajax(self):
        return self.is_xhr

    @property
    def remote_addr(self):
        return self.environ.get('HTTP_X_REAL_IP', super(Request, self).remote_addr)

from flask.wrappers import Request as RequestFlask


class Request(RequestFlask):
    """Extended Flask request class used by all FlaskCBV views.

    Adds convenience properties for AJAX detection and real client IP
    resolution behind a reverse proxy.
    """

    @property
    def is_ajax(self):
        """True if the request carries the ``X-Requested-With: XMLHttpRequest`` header."""
        return self.is_xhr

    @property
    def remote_address(self):
        """Client IP address, preferring the ``X-Real-IP`` proxy header.

        Returns:
            str: Value of ``HTTP_X_REAL_IP`` environ key when present,
                otherwise ``REMOTE_ADDR``.

        Note:
            Only trust ``HTTP_X_REAL_IP`` when the application sits behind
            a trusted reverse proxy that sets this header.
        """
        return self.environ.get('HTTP_X_REAL_IP', self.remote_addr)

from flask.wrappers import Request as RequestFlask
try:
    from flaskcbv.conf import settings
except Exception:
    settings = None


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
        """Client IP address, with optional ``X-Real-IP`` proxy header support.

        ``X-Real-IP`` is only trusted when the direct TCP peer (``REMOTE_ADDR``)
        is listed in ``TRUSTED_PROXIES`` setting.  If the list is empty or the
        peer is not trusted, ``REMOTE_ADDR`` is returned as-is.

        Configure in settings::

            TRUSTED_PROXIES = ['127.0.0.1', '10.0.0.1']

        Returns:
            str: Real client IP when behind a trusted proxy, otherwise ``REMOTE_ADDR``.
        """
        trusted = getattr(settings, 'TRUSTED_PROXIES', []) if settings is not None else []
        if trusted and self.remote_addr in trusted:
            return self.environ.get('HTTP_X_REAL_IP', self.remote_addr)
        return self.remote_addr

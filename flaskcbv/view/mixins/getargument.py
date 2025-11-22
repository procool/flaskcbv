import logging


class getArgumentMixin(object):
    """Mixin that provides unified access to request parameters.

    Searches GET, POST, cookie, and session sources in order, returning
    the first match found via ``get_argument_smart()``.
    """

    def __get_argument_get(self, key):
        return self.request.args[key]

    def __get_argument_post(self, key):
        return self.request.form[key]

    def __get_argument_cookie(self, key):
        return self.request.cookies[key]


    def __get_argument_session(self, key):
        return self.session[key]


    def get_argument_smart(self, key, as_get=True, as_post=True, as_session=False, as_cookie=False):
        """Look up *key* across multiple request sources.

        Sources are checked in the order: GET → POST → cookie → session.
        The first source that contains *key* wins.

        Args:
            key (str): Parameter name to look up.
            as_get (bool): Search query string. Default True.
            as_post (bool): Search form data. Default True.
            as_session (bool): Search Flask session. Default False.
            as_cookie (bool): Search cookies. Default False.

        Returns:
            str: The parameter value from the first matching source.

        Raises:
            KeyError: If *key* is not found in any enabled source.
        """
        if as_get:
            try:
                return self.__get_argument_get(key)
            except KeyError:
                pass

        if as_post:
            try:
                return self.__get_argument_post(key)
            except KeyError:
                pass

        if as_cookie:
            try:
                return self.__get_argument_cookie(key)
            except KeyError:
                pass

        if as_session:
            try:
                return self.__get_argument_session(key)
            except KeyError:
                pass

        raise KeyError(key)



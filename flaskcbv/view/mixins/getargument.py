import logging

## Distinguishes "no default given" from an explicit default of None.
_NO_DEFAULT = object()


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


    def get_argument_smart(self, key, as_get=True, as_post=True, as_session=False, as_cookie=False,
                           default=_NO_DEFAULT):
        """Look up *key* across multiple request sources.

        Sources are checked in the order: GET → POST → cookie → session.
        The first source that contains *key* wins.

        Args:
            key (str): Parameter name to look up.
            as_get (bool): Search query string. Default True.
            as_post (bool): Search form data. Default True.
            as_session (bool): Search Flask session. Default False.
            as_cookie (bool): Search cookies. Default False.
            default: Returned when *key* is found nowhere. Without it a
                missing key raises KeyError, as before.

        Returns:
            str: The parameter value from the first matching source, or
            *default*.

        Raises:
            KeyError: If *key* is not found and no *default* was given.
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

        if default is not _NO_DEFAULT:
            return default
        raise KeyError(key)



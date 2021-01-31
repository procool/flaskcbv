import logging


class getArgumentMixin(object):

    def __get_argument_get(self, key):
        return self.request.args[key]

    def __get_argument_post(self, key):
        return self.request.form[key]

    def __get_argument_cookie(self, key):
        return self.request.cookies[key]


    def __get_argument_session(self, key):
        return self.session[key]


    def get_argument_smart(self, key, as_get=True, as_post=True, as_session=False, as_cookie=False):
        if as_get:
            try: return self.__get_argument_get(key)
            except: pass

        if as_post:
            try: return self.__get_argument_post(key)
            except: pass

        if as_cookie:
            try: return self.__get_argument_cookie(key)
            except: pass


        if as_session:
            try: return self.__get_argument_session(key)
            except: pass

        raise KeyError(key)



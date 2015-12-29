import json
import logging

class JSONMixin(object):
    json_cls = None
    json_default = None
    onlyjson=True


    def json_response_include(self):
        return None

    def json_response_exclude(self):
        return ['request']

    def get_json_cls(self):
        return self.json_cls

    def get_json_indent(self):
        return None

    def get_json_kwargs(self, **kwargs):
        kwargs.update({
            'default': self.json_default, 
            'cls' : self.get_json_cls(), 
            'indent' : self.get_json_indent()
        })
        return kwargs

    def get_context_data(self, *args, **kwargs):
        try: return super(JSONMixin, self).get_context_data(*args, **kwargs)
        except: return kwargs


    def get_as_json_data(self, **data):
        answ = {'errno': 0, 'error': 'Ok', 'details': '',}

        try: context = self.get_context_data()
        except Exception as err: 
            self.test_abort_exception(err)
            context = {
                'errno': -1,
                'error': 'Failed',
                'details': str(err),
            }

        answ.update(data)

        include_ = self.json_response_include()
        if include_ is not None:
            for item in include_:
                try: answ[item] = context[item]
                except: pass
        else:
            answ.update(context)


        for item in self.json_response_exclude():
            try: del answ[item]
            except: pass
        return answ

    def get_as_json(self, **data):
        return json.dumps(self.get_as_json_data(**data), **self.get_json_kwargs())


    def json_error(self, errno=-1, error='Failed', details='', **data):
        return self.get_as_json(errno=errno, error=error, details=details, **data)


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



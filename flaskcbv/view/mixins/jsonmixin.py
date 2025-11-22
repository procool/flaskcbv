import json
import logging

class JSONMixin(object):
    """Mixin that serialises the view context to a JSON response.

    Combine with ``View`` or ``TemplateView`` to return JSON::

        class MyAPI(JSONMixin, View):
            def get_context_data(self, **kwargs):
                return {'items': [1, 2, 3]}

            def dispatch(self, request, *args, **kwargs):
                return Response(self.get_as_json())

    Attributes:
        json_cls: Custom JSON encoder class passed to ``json.dumps``.
        json_default: Default serialiser callable for unknown types.
        onlyjson (bool): Marker flag; not used internally, reserved.
    """

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
        try:
            return super(JSONMixin, self).get_context_data(*args, **kwargs)
        except AttributeError:
            return kwargs


    def get_as_json_data(self, **data):
        answ = {'errno': 0, 'error': 'Ok', 'details': '',}

        try:
            context = self.get_context_data()
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
                try:
                    answ[item] = context[item]
                except KeyError:
                    pass
        else:
            answ.update(context)

        for item in self.json_response_exclude():
            try:
                del answ[item]
            except KeyError:
                pass
        return answ

    def get_as_json(self, **data):
        """Serialise the view context to a JSON string.

        Args:
            **data: Extra key/value pairs merged into the response dict.

        Returns:
            str: JSON-encoded response body.
        """
        return json.dumps(self.get_as_json_data(**data), **self.get_json_kwargs())


    def json_error(self, errno=-1, error='Failed', details='', **data):
        """Return a JSON-encoded error response.

        Args:
            errno (int): Numeric error code. Default -1.
            error (str): Short error label. Default ``'Failed'``.
            details (str): Extended error description.
            **data: Additional fields included in the response dict.

        Returns:
            str: JSON string with ``errno``, ``error``, and ``details`` fields.
        """
        return self.get_as_json(errno=errno, error=error, details=details, **data)




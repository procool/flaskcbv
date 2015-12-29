import os

from flask import request, render_template, session
from flask import abort, redirect, url_for
from flaskcbv.response import Response
from flaskcbv.core.base import get_flask


class View(object):
    options = {}
    AVALIBLE_METHODS = ["GET", "POST", "OPTIONS", "HEAD",]
    decorators = []

    __flask = get_flask()

    def __init__(self, options=None, **kwargs):

        self.request = request
        self.url = None
        self.current_url = None
        if options is not None:
            self.options = options

        if not 'methods' in self.options:
            self.options['methods'] = []
            for attr in dir(self):
                if attr.upper() in self.AVALIBLE_METHODS:
                    self.options['methods'].append(attr.upper())
        self.session = session


    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """Converts the class into an actual view function that can be used
        with the routing system.  Internally this generates a function on the
        fly which will instantiate the :class:`View` on each request and call
        the :meth:`dispatch_request` method on it.
                
        The arguments passed to :meth:`as_view` are forwarded to the
        constructor of the class.
        """
        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            self.url = view.url
            self.current_url = view.current_url
            return self.prepare(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)
                
        # we attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__flask = cls.__flask
        view.AVALIBLE_METHODS = cls.AVALIBLE_METHODS
        view.options = cls.options
        return view



    def prepare(self, *args, **kwargs):
        response = self.dispatch(request, *args, **kwargs)
        return response.render(headers=self.get_headers())

    def dispatch(self, request, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        # if the request method is HEAD and we don't have a handler for it
        # retry with GET

        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        if meth is not None:
            return meth(request, *args, **kwargs)

        abort(405)


    def get(self, request, *args, **kwargs):
        return Response("(GET) It works on FlaskCBV!")
    
    def post(self, request, *args, **kwargs):
        return Response("(POST) It works on FlaskCBV!")


    ## Returns response headers:
    def get_headers(self, **kwargs):
        return kwargs


 

    ## Returns current url:
    def get_current_url(self):
        return self.current_url


    ## Returns all defined urls:
    @classmethod
    def get_all_urls(cls_, **kwargs):
        return cls_.__flask.get_all_urls(**kwargs)


    @staticmethod
    def is_abort_exception(ex):
        if hasattr(ex, 'code'):
            return True
        if hasattr(ex, 'get_headers'):
            return True
        if hasattr(ex, 'response'):
            return True
        return False

    @classmethod
    def test_abort_exception(cls, ex):
        if cls.is_abort_exception(ex):
            raise ex
    


class TemplateMixin(View):
    template = None

    def __init__(self, template=None, **kwargs):
        if template is not None:
            self.template = template

        super(TemplateMixin, self).__init__(**kwargs)


    def get_template_name(self, template=None):
        if template is None:
            template = self.template
        return template

    def get_context_data(self):
        return {
        }

    def render_template(self, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return render_template(self.get_template_name(), **context)


class TemplateView(TemplateMixin, View):
    def get_context_data(self):
        context = super(TemplateView, self).get_context_data()
        context['request'] = self.request
        return context

    def get(self, request, *args, **kwargs):
        data = self.render_template(*args, **kwargs)
        return Response(data)

    def dispatch(self, request, *args, **kwargs):
        return super(TemplateView, self).dispatch(request, *args, **kwargs)



class TemplateIsAjaxView(TemplateView):
    def get_template_name(self, is_ajax=None, **kwargs):
        template = super(TemplateIsAjaxView, self).get_template_name(**kwargs)
        
        self.__path = ''
        self.__path_ajax = ''
        fl, ext = os.path.splitext(template)
        if fl.endswith('-ajax'):
            self.__path_ajax = fl + ext
            self.__path = fl[0:-5] + ext
        else:
            self.__path = fl + ext
            self.__path_ajax = "%s-ajax%s" % (fl, ext)

        if is_ajax or self.request.is_ajax:
            return self.__path_ajax

        return self.__path




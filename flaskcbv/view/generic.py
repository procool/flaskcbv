import os

from flask import request, render_template, session
from flask import abort, redirect, url_for
from flaskcbv.response import Response
from flaskcbv.core.base import get_flask


class View(object):
    """Base class-based view.

    Subclass this and define ``get()``, ``post()``, or other HTTP-method
    handlers.  Register with Flask via ``Url`` and ``make_urls()``::

        class MyView(View):
            def get(self, request, *args, **kwargs):
                return Response('hello')

        # in urls.py:
        namespases = make_urls(Url('/', MyView(), name='index'))

    Attributes:
        options (dict): Extra keyword arguments forwarded to
            ``app.add_url_rule()``, e.g. ``{'methods': ['GET']}``.
        AVALIBLE_METHODS (list): HTTP methods this view may handle.
            Methods not in this list result in a 405 response.
        decorators (list): View-level decorators applied by ``as_view()``.
    """

    options = {}
    AVALIBLE_METHODS = ["GET", "POST", "OPTIONS", "HEAD",]
    decorators = []

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
        view.AVALIBLE_METHODS = cls.AVALIBLE_METHODS
        view.options = cls.options
        return view



    def prepare(self, *args, **kwargs):
        """Entry point called by Flask on every incoming request.

        Calls ``dispatch()``, then renders the returned ``Response``
        with headers from ``get_headers()``.

        Returns:
            flask.Response: The rendered HTTP response.
        """
        response = self.dispatch(request, *args, **kwargs)
        return response.render(headers=self.get_headers())

    def dispatch(self, request, *args, **kwargs):
        """Route the request to the correct HTTP-method handler.

        Resolves ``request.method`` to a same-named instance method
        (``get``, ``post``, etc.).  HEAD falls back to ``get`` when no
        explicit handler is defined.  Returns 405 if the method is not
        available.

        Args:
            request: The current Flask request object.
            *args: Positional URL rule captures.
            **kwargs: Named URL rule captures.

        Returns:
            Response: Result of the matched handler.
        """
        meth = getattr(self, request.method.lower(), None)
        if isinstance(meth, dict):
            meth = getattr(self, 'method_%s' % request.method.lower(), None)

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
        """Return headers to include in the HTTP response.

        Override to add custom headers.  The result is merged with
        ``DEFAULT_HEADERS`` from settings inside ``Response.render()``.

        Returns:
            dict: Header name → value mapping.
        """
        return kwargs


 

    ## Returns current url:
    def get_current_url(self):
        return self.current_url


    ## Returns all defined urls:
    @classmethod
    def get_all_urls(cls_, **kwargs):
        """Return all URL endpoints registered with the Flask application.

        Args:
            **kwargs: Forwarded to ``Flask.get_all_urls()``.
                Pass ``with_defs=True`` to get the full view-function dict.

        Returns:
            list: Endpoint names, or dict when ``with_defs=True``.
        """
        return get_flask().get_all_urls(**kwargs)


    @staticmethod
    def is_abort_exception(ex):
        """Check whether *ex* is a Flask HTTP exception (abort-style).

        Args:
            ex (Exception): The exception to inspect.

        Returns:
            bool: True if *ex* looks like a werkzeug HTTPException.
        """
        if hasattr(ex, 'code'):
            return True
        if hasattr(ex, 'get_headers'):
            return True
        if hasattr(ex, 'response'):
            return True
        return False

    @classmethod
    def test_abort_exception(cls, ex):
        """Re-raise *ex* if it is a Flask abort-style exception.

        Use inside ``get_as_json_data`` or similar error-handling code
        to let HTTP errors propagate while swallowing ordinary exceptions.

        Args:
            ex (Exception): The exception to test.

        Raises:
            ex: Re-raised if ``is_abort_exception(ex)`` returns True.
        """
        if cls.is_abort_exception(ex):
            raise ex
    


class TemplateMixin(View):
    """Mixin that adds Jinja2 template rendering to a View.

    Attributes:
        template (str): Path to the Jinja2 template, relative to
            one of the configured template directories.
    """

    template = None

    def __init__(self, template=None, **kwargs):
        if template is not None:
            self.template = template

        super(TemplateMixin, self).__init__(**kwargs)


    def get_template_name(self, template=None):
        """Return the template path to render.

        Args:
            template (str, optional): Override the class-level template.

        Returns:
            str: Template path.
        """
        if template is None:
            template = self.template
        return template

    def get_context_data(self, **kwargs):
        """Return the template context dictionary.

        Override to inject additional variables.

        Returns:
            dict: Context passed to the template.
        """
        return dict(kwargs)

    def render_template(self, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return render_template(self.get_template_name(), **context)


class TemplateView(TemplateMixin, View):
    """View that renders a Jinja2 template on GET requests.

    Adds ``request`` to the template context automatically.
    Override ``get_context_data()`` to supply additional variables::

        class MyView(TemplateView):
            template = 'app/index.tpl'

            def get_context_data(self, **kwargs):
                ctx = super().get_context_data(**kwargs)
                ctx['title'] = 'Hello'
                return ctx
    """

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['request'] = self.request
        return context

    def get(self, request, *args, **kwargs):
        data = self.render_template(*args, **kwargs)
        return Response(data)

    def dispatch(self, request, *args, **kwargs):
        return super(TemplateView, self).dispatch(request, *args, **kwargs)



class TemplateIsAjaxView(TemplateView):
    """TemplateView that serves different templates for AJAX vs normal requests.

    For a template named ``index.tpl``, AJAX requests receive
    ``index-ajax.tpl``; for ``index-ajax.tpl``, normal requests
    receive ``index.tpl``.  Detection is based on ``request.is_ajax``.
    """

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




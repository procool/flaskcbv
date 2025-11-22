
class Url(object):
    """Descriptor that binds a URL path to a view object or include.

    Args:
        url (str): URL path, e.g. ``'/users/<int:id>'``.
        obj: A ``View`` instance, an ``as_view()`` callable, or the
            result of ``include()`` for nested URL configs.
        name (str, optional): Endpoint name used for ``url_for()`` lookups.
        namespace (str, optional): Namespace prefix set by ``include()``.
        namespace_descr (str): Human-readable namespace description.
    """

    def __init__(self, url, obj, name=None, namespace=None, namespace_descr=''):
        self.url = url
        self.obj = obj
        self.__name = name
        self.namespace = namespace
        self.namespace_descr = namespace_descr

    @property
    def name(self):
        return self.__name

    @property
    def endpoint(self):
        """Full endpoint string, including namespace prefix when set.

        Returns:
            str: E.g. ``'main:index'`` or ``'index'``.

        Raises:
            Exception: If ``name`` was not provided.
        """
        if self.name is None:
            raise Exception("name attr is not defined!")
        ns = self.namespace is not None and "%s:" % self.namespace or ''
        return "%s%s" % (ns, self.name)




def make_urls(*namespases):
    """Build the URL table consumed by ``CBVCore.make_urls()``.

    Each ``Url`` entry is expanded into a 5-element list:
    ``[Url, path, endpoint, callable, options]``.

    Args:
        *namespases: ``Url`` instances to register.

    Returns:
        list: Flat list of URL entries ready for ``add_url_rule()``.

    Example:
        ::

            namespases = make_urls(
                Url('/',      IndexView(), name='index'),
                Url('/about', AboutView(), name='about'),
            )
    """
    urls = []

    for url in namespases:
        if isinstance(url.obj, (list, tuple)):
            for url_ in url.obj:
                url_[0].url = '%s%s' % (url.url, url_[0].url)
                url_[1] = url_[0].url
            urls += list(url.obj)
            continue
         
        ## as_view:                
        as_view = url.obj.__class__.__name__ == 'function' and True or False

        endpoint = url.obj.options.pop('endpoint', None)
        if endpoint is None:
            try:
                endpoint = url.endpoint
            except Exception:
                if as_view:
                    endpoint = url.obj.__name__
                else:
                    endpoint = url.obj.__class__.__name__
        def_ = as_view and url.obj or url.obj.prepare
        urls.append([url, url.url, endpoint, def_, url.obj.options])
    return urls



def include(namespases, namespace=None, description=None, **kwargs):
    """Attach a namespace to an imported URL list.

    Use inside a parent ``urls.py`` to mount a sub-application under a
    named namespace so its endpoints are reachable as ``namespace:name``::

        from apps.blog import urls as blog_urls

        namespases = make_urls(
            Url('/blog', include(blog_urls.namespases, namespace='blog')),
        )

    Args:
        namespases (list): URL table returned by ``make_urls()`` from another module.
        namespace (str, optional): Namespace string to assign to every entry.
        description (str, optional): Human-readable label for the namespace.

    Returns:
        list: The same URL table with namespace set on each ``Url`` object.
    """
    for ns in namespases:
        url = ns[0]
        url.namespace = namespace
        url.namespace_descr = description or namespace.upper() or ''
        try:
            ns[2] = url.endpoint
        except Exception:
            pass
    return namespases


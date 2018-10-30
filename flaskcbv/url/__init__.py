
class Url(object):
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
        if self.name is None:
            raise(Exception("name attr is not defined!"))
        ns = self.namespace is not None and "%s:" % self.namespace or ''
        return "%s%s" % (ns, self.name)




def make_urls(*namespases):
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
            except:
                if as_view:
                    endpoint = url.obj.__name__
                else:
                    endpoint = url.obj.__class__.__name__
        def_ = as_view and url.obj or url.obj.prepare
        urls.append([url, url.url, endpoint, def_, url.obj.options])
    return urls



def include(namespases, namespace=None, description=None, **kwargs):
    for ns in namespases:
        url = ns[0]
        url.namespace = namespace
        url.namespace_descr = description or namespace.upper() or ''
        try: ns[2] = url.endpoint
        except: pass
    return namespases


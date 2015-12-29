from jinja2 import nodes
from jinja2.ext import Extension

class loadExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['load'])

    def __init__(self, environment):
        super(loadExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]

        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))
        self._load(args[0].value, 0, lambda: '')

        return nodes.CallBlock(self.call_method('_empty', args),
                               [], [], "").set_lineno(lineno)


    def _load(self, name, timeout, caller):
        name_ = "templatetags.%s" % name
        mod_ = getattr(__import__(name_), name)
        for extension in dir(mod_):
            extension = getattr(mod_, extension)
            if not hasattr(extension, 'enabled'):
                continue
            if not extension.enabled:
                continue
            self.environment.add_extension(extension)
            print self.environment.extensions
        
        return caller()



    


    def _empty(self, name, timeout, caller):
        return caller()

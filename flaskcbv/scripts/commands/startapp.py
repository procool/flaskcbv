import os


_VIEWS_PY = '''\
from flaskcbv.view import View
from flaskcbv.response import Response


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return Response(open(self.get_template_path()).read())

    def get_template_path(self):
        import os
        here = os.path.dirname(__file__)
        return os.path.join(here, 'templates', '{name}', 'index.tpl')
'''

_URLS_PY = '''\
from flaskcbv.url import Url, make_urls
from .views import IndexView

namespases = make_urls(
    Url('/', IndexView(), name='index'),
)
'''

_INDEX_TPL = 'It works! App: {name}\n'


def _write(path, content):
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


class cmdStartApp(object):
    def get_cli_commands(self):
        commands = super(cmdStartApp, self).get_cli_commands()
        commands['startapp'] = self.__main
        return commands

    def set_cli_parser_args(self, parser, *args, **kwargs):
        super(cmdStartApp, self).set_cli_parser_args(parser, *args, **kwargs)
        parser.add_argument(
            'name',
            nargs='?',
            default=None,
            help='Application name (required for startapp)',
        )

    def cli_process_args(self, namespace, *args, **kwargs):
        super(cmdStartApp, self).cli_process_args(namespace, *args, **kwargs)
        self._startapp_name = getattr(namespace, 'name', None)

    def __main(self):
        name = getattr(self, '_startapp_name', None)
        if not name:
            raise Exception('Usage: flaskcbv startapp <name>')

        base = os.path.join('apps', name)
        if os.path.exists(base):
            raise Exception('Directory already exists: %s' % base)

        _write(os.path.join(base, '__init__.py'), '')
        _write(os.path.join(base, 'views.py'), _VIEWS_PY.format(name=name))
        _write(os.path.join(base, 'urls.py'), _URLS_PY)
        _write(os.path.join(base, 'templates', name, 'index.tpl'), _INDEX_TPL.format(name=name))

        print('App "%s" created in %s' % (name, os.path.abspath(base)))

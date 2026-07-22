## URL configuration used by the test engine (CBVCore.make_urls does
## a bare 'from urls import namespaces', so this file must be on sys.path).

from flaskcbv.url import Url, make_urls
from flaskcbv.view import View
from flaskcbv.response import Response


class _IndexView(View):
    def get(self, request, *args, **kwargs):
        return Response('index ok')

    def post(self, request, *args, **kwargs):
        return Response('post ok')


class _AboutView(View):
    def get(self, request, *args, **kwargs):
        return Response('about ok')


namespaces = make_urls(
    Url('/',      _IndexView(), name='index'),
    Url('/about', _AboutView(), name='about'),
)

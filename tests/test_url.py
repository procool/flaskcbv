import pytest
from flaskcbv.url import Url, make_urls, include
from flaskcbv.view import View
from flaskcbv.response import Response


class _DummyView(View):
    def get(self, request, *args, **kwargs):
        return Response('dummy')


class TestUrlClass:
    def test_url_stores_path(self):
        u = Url('/foo', _DummyView(), name='foo')
        assert u.url == '/foo'

    def test_url_stores_name(self):
        u = Url('/foo', _DummyView(), name='foo')
        assert u.name == 'foo'

    def test_endpoint_without_namespace(self):
        u = Url('/foo', _DummyView(), name='foo')
        assert u.endpoint == 'foo'

    def test_endpoint_with_namespace(self):
        u = Url('/foo', _DummyView(), name='foo', namespace='ns')
        assert u.endpoint == 'ns:foo'

    def test_endpoint_raises_without_name(self):
        u = Url('/foo', _DummyView())
        with pytest.raises(Exception):
            _ = u.endpoint

    def test_no_name_is_none(self):
        u = Url('/foo', _DummyView())
        assert u.name is None


class TestMakeUrls:
    def test_returns_list(self):
        result = make_urls(
            Url('/a', _DummyView(), name='a'),
        )
        assert isinstance(result, list)

    def test_single_url_structure(self):
        u = Url('/a', _DummyView(), name='a')
        result = make_urls(u)
        assert len(result) == 1
        ## Each entry: [Url, path, endpoint, callable, options]
        entry = result[0]
        assert entry[1] == '/a'
        assert entry[2] == 'a'
        assert callable(entry[3])

    def test_multiple_urls(self):
        result = make_urls(
            Url('/x', _DummyView(), name='x'),
            Url('/y', _DummyView(), name='y'),
        )
        assert len(result) == 2
        endpoints = [e[2] for e in result]
        assert 'x' in endpoints
        assert 'y' in endpoints


class TestInclude:
    def test_include_sets_namespace(self):
        inner = make_urls(
            Url('/inner', _DummyView(), name='inner'),
        )
        result = include(inner, namespace='myns')
        ## After include, each entry's endpoint should carry namespace
        u = result[0][0]
        assert u.namespace == 'myns'

    def test_include_sets_endpoint_in_entry(self):
        inner = make_urls(
            Url('/inner', _DummyView(), name='inner'),
        )
        result = include(inner, namespace='app')
        assert result[0][2] == 'app:inner'

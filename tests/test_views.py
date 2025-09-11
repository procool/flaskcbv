import pytest
from flaskcbv.view import View
from flaskcbv.response import Response


class TestViewHTTPMethods:
    def test_get_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200
        assert b'index ok' in r.data

    def test_post_returns_200(self, client):
        r = client.post('/')
        assert r.status_code == 200
        assert b'post ok' in r.data

    def test_method_not_allowed(self, client):
        ## _IndexView only defines get/post; DELETE should return 405
        r = client.delete('/')
        assert r.status_code == 405

    def test_second_route(self, client):
        r = client.get('/about')
        assert r.status_code == 200
        assert b'about ok' in r.data

    def test_unknown_route_returns_404(self, client):
        r = client.get('/nonexistent')
        assert r.status_code == 404


class TestViewAsView:
    def test_as_view_returns_callable(self):
        fn = View.as_view('test_view')
        assert callable(fn)

    def test_as_view_sets_name(self):
        fn = View.as_view('my_view')
        assert fn.__name__ == 'my_view'

    def test_as_view_sets_view_class(self):
        fn = View.as_view('cls_view')
        assert fn.view_class is View

    def test_as_view_inherits_available_methods(self):
        fn = View.as_view('methods_view')
        assert fn.AVALIBLE_METHODS == View.AVALIBLE_METHODS


class TestViewGetAllUrls:
    def test_returns_list(self, app_ctx):
        urls = View.get_all_urls()
        assert isinstance(urls, list)

    def test_contains_registered_endpoints(self, app_ctx):
        urls = View.get_all_urls()
        assert 'index' in urls
        assert 'about' in urls


class TestViewAbortException:
    def test_abort_exception_detected_by_code(self, req_ctx):
        class FakeAbort(Exception):
            code = 404
        assert View.is_abort_exception(FakeAbort()) is True

    def test_regular_exception_not_abort(self, req_ctx):
        assert View.is_abort_exception(ValueError('oops')) is False

    def test_test_abort_exception_reraises(self, req_ctx):
        class FakeAbort(Exception):
            code = 500
        with pytest.raises(FakeAbort):
            View.test_abort_exception(FakeAbort())

    def test_test_abort_exception_ignores_regular(self, req_ctx):
        ## Should not raise for non-abort exceptions
        View.test_abort_exception(ValueError('nope'))

import unittest.mock as mock
import pytest
from flaskcbv.view import View
from flaskcbv.view.generic import TemplateIsAjaxView
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
        assert fn.AVAILABLE_METHODS == View.AVAILABLE_METHODS
        assert fn.AVALIBLE_METHODS == View.AVALIBLE_METHODS


class TestViewOptionsIsolation:
    def test_instances_do_not_share_options(self):
        ## Class-level options dict must not be mutated by instance __init__
        class ViewA(View):
            pass

        class ViewB(View):
            AVAILABLE_METHODS = ['POST']

        a = ViewA.__new__(ViewA)
        b = ViewB.__new__(ViewB)
        ## options class attr must still be empty after instantiation
        assert ViewA.options == {}
        assert ViewB.options == {}

    def test_instance_options_are_independent(self, req_ctx):
        class ViewA(View):
            pass

        class ViewB(View):
            AVAILABLE_METHODS = ['POST']

        a = ViewA()
        b = ViewB()
        assert a.options is not b.options
        assert 'GET' in a.options['methods']
        assert b.options['methods'] == ['POST']

    def test_class_options_not_mutated_after_init(self, req_ctx):
        class ViewC(View):
            options = {'strict_slashes': False}

        ViewC()
        ## class-level options must not get 'methods' injected into it
        assert 'methods' not in ViewC.options


class TestViewMethodsAlias:
    def test_available_methods_synced_from_available(self):
        ## subclass defines new name -> old name auto-set
        class ViewNew(View):
            AVAILABLE_METHODS = ['GET']

        assert ViewNew.AVALIBLE_METHODS == ['GET']

    def test_available_methods_synced_from_deprecated(self):
        ## subclass defines old (deprecated) name -> new name auto-set
        class ViewOld(View):
            AVALIBLE_METHODS = ['POST']

        assert ViewOld.AVAILABLE_METHODS == ['POST']

    def test_base_aliases_are_same_object(self):
        assert View.AVAILABLE_METHODS is View.AVALIBLE_METHODS

    def test_both_defined_not_overwritten(self):
        ## if subclass defines both, neither is overwritten
        class ViewBoth(View):
            AVAILABLE_METHODS = ['GET']
            AVALIBLE_METHODS = ['POST']

        assert ViewBoth.AVAILABLE_METHODS == ['GET']
        assert ViewBoth.AVALIBLE_METHODS == ['POST']


def _make_ajax_view(template, is_ajax):
    ## TemplateIsAjaxView needs self.request; mock it to avoid Werkzeug
    ## version issues (is_ajax was removed in Werkzeug 2.1).
    v = TemplateIsAjaxView.__new__(TemplateIsAjaxView)
    v.template = template
    v.request = mock.Mock(is_ajax=is_ajax)
    return v


class TestTemplateIsAjaxView:
    def test_ajax_request_returns_ajax_template(self):
        v = _make_ajax_view('index.html', is_ajax=True)
        assert v.get_template_name() == 'index-ajax.html'

    def test_non_ajax_request_returns_normal_template(self):
        v = _make_ajax_view('index.html', is_ajax=False)
        assert v.get_template_name() == 'index.html'

    def test_explicit_is_ajax_true_overrides_request(self):
        v = _make_ajax_view('page.html', is_ajax=False)
        assert v.get_template_name(is_ajax=True) == 'page-ajax.html'

    def test_explicit_is_ajax_false_returns_normal(self):
        v = _make_ajax_view('page.html', is_ajax=False)
        assert v.get_template_name(is_ajax=False) == 'page.html'

    def test_ajax_template_with_extension(self):
        v = _make_ajax_view('views/detail.tpl', is_ajax=True)
        assert v.get_template_name() == 'views/detail-ajax.tpl'

    def test_inverted_ajax_template_normal_request(self):
        ## if the template itself is already '-ajax', non-ajax gets the base name
        v = _make_ajax_view('index-ajax.html', is_ajax=False)
        assert v.get_template_name() == 'index.html'

    def test_inverted_ajax_template_ajax_request(self):
        v = _make_ajax_view('index-ajax.html', is_ajax=True)
        assert v.get_template_name() == 'index-ajax.html'


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

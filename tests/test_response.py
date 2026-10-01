import pytest
from flaskcbv.response import Response, ResponseNotModified, ResponseRedirect


class TestResponseString:
    def test_plain_string_body(self, req_ctx):
        r = Response('hello')
        flask_r = r.render()
        assert flask_r.data == b'hello'

    def test_empty_string(self, req_ctx):
        r = Response('')
        flask_r = r.render()
        assert flask_r.status_code == 200

    def test_status_200(self, req_ctx):
        r = Response('ok')
        flask_r = r.render()
        assert flask_r.status_code == 200


class TestResponseCallable:
    def test_callable_is_invoked_at_render(self, req_ctx):
        called = []

        def body():
            called.append(1)
            return 'from callable'

        r = Response(body)
        assert called == []        ## not called yet
        flask_r = r.render()
        assert called == [1]       ## called during render
        assert flask_r.data == b'from callable'

    def test_lambda_callable(self, req_ctx):
        r = Response(lambda: 'lambda body')
        assert r.render().data == b'lambda body'


class TestResponseGenerator:
    def test_generator_returns_streamed_response(self, client):
        ## Use the test client (full app context) because stream_with_context
        ## needs an active request.
        def gen():
            yield 'part1'
            yield 'part2'

        r = Response(gen())
        flask_r = r.render()
        ## Streamed responses use transfer-encoding chunked or just work as
        ## iterables; get_data(as_text=True) forces consumption.
        body = flask_r.get_data(as_text=True)
        assert 'part1' in body
        assert 'part2' in body


class TestResponseHeaders:
    def test_add_header_stored(self, req_ctx):
        r = Response('x')
        r.add_header('X-Custom', 'value')
        assert r.custom_headers['X-Custom'] == 'value'

    def test_add_header_appears_in_rendered_response(self, req_ctx):
        r = Response('x')
        r.add_header('X-Foo', 'bar')
        flask_r = r.render()
        assert flask_r.headers['X-Foo'] == 'bar'

    def test_render_extra_headers_merged(self, req_ctx):
        r = Response('x')
        flask_r = r.render(headers={'X-Extra': 'yes'})
        assert flask_r.headers['X-Extra'] == 'yes'

    def test_add_header_and_render_headers_both_present(self, req_ctx):
        r = Response('x')
        r.add_header('X-A', '1')
        flask_r = r.render(headers={'X-B': '2'})
        assert flask_r.headers['X-A'] == '1'
        assert flask_r.headers['X-B'] == '2'


class TestResponseRedirect:
    def test_redirect_default_302(self, req_ctx):
        r = ResponseRedirect('/target')
        flask_r = r.render()
        assert flask_r.status_code == 302
        assert '/target' in flask_r.headers['Location']

    def test_redirect_custom_code(self, req_ctx):
        r = ResponseRedirect('/gone', code=301)
        flask_r = r.render()
        assert flask_r.status_code == 301

    def test_redirect_status_kwarg_is_honoured(self, req_ctx):
        ## `status=` must not be silently ignored on a redirect.
        assert ResponseRedirect('/moved', status=301).render().status_code == 301

    def test_redirect_header_forwarded(self, req_ctx):
        r = ResponseRedirect('/x')
        r.add_header('X-Redir', 'yes')
        flask_r = r.render()
        assert flask_r.headers['X-Redir'] == 'yes'


class TestResponseStatus:
    def test_custom_status(self, req_ctx):
        r = Response('created', status=201)
        assert r.render().status_code == 201

    def test_status_with_generator(self, client):
        def gen():
            yield 'x'
        flask_r = Response(gen(), status=206).render()
        assert flask_r.status_code == 206
        assert flask_r.get_data(as_text=True) == 'x'

    def test_status_keeps_headers(self, req_ctx):
        r = Response('', status=404)
        r.add_header('X-Why', 'gone')
        flask_r = r.render()
        assert flask_r.status_code == 404
        assert flask_r.headers['X-Why'] == 'gone'


class TestResponseNotModified:
    def test_status_304(self, req_ctx):
        assert ResponseNotModified().render().status_code == 304

    def test_etag_header(self, req_ctx):
        flask_r = ResponseNotModified(etag='"7-3"').render()
        assert flask_r.headers['ETag'] == '"7-3"'

    def test_body_is_empty_on_the_wire(self, req_ctx):
        ## Run the rendered response as WSGI: registering a route here would
        ## depend on no request having been served yet by the shared app.
        from werkzeug.test import EnvironBuilder, run_wsgi_app
        flask_r = ResponseNotModified(etag='"x"').render()
        app_iter, status, headers = run_wsgi_app(flask_r, EnvironBuilder().get_environ())
        assert status.startswith('304')
        assert b''.join(app_iter) == b''
        assert headers.get('ETag') == '"x"'
        assert 'Content-Length' not in headers

    def test_status_is_a_class_default(self):
        ## A subclass that overrides __init__ without super() must still render.
        assert Response.status is None

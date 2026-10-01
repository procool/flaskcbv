import pytest
from flask import request

from flaskcbv.view.mixins.getargument import getArgumentMixin


class _View(getArgumentMixin):
    def __init__(self, session=None):
        self.request = request
        self.session = session or {}


class TestGetArgumentSmart:
    def test_reads_query_string(self, app):
        with app.test_request_context('/?a=1'):
            assert _View().get_argument_smart('a') == '1'

    def test_reads_form(self, app):
        with app.test_request_context('/', method='POST', data={'b': '2'}):
            assert _View().get_argument_smart('b') == '2'

    def test_query_wins_over_form(self, app):
        with app.test_request_context('/?k=get', method='POST', data={'k': 'post'}):
            assert _View().get_argument_smart('k') == 'get'

    def test_missing_raises_key_error_without_default(self, app):
        ## Existing callers rely on KeyError (try/except around the call).
        with app.test_request_context('/'):
            with pytest.raises(KeyError):
                _View().get_argument_smart('nope')

    def test_missing_returns_default(self, app):
        with app.test_request_context('/'):
            assert _View().get_argument_smart('nope', default='x') == 'x'

    def test_default_none_is_honoured(self, app):
        with app.test_request_context('/'):
            assert _View().get_argument_smart('nope', default=None) is None

    def test_found_value_beats_default(self, app):
        with app.test_request_context('/?a=1'):
            assert _View().get_argument_smart('a', default='x') == '1'

    def test_disabled_source_falls_to_default(self, app):
        with app.test_request_context('/?a=1'):
            assert _View().get_argument_smart('a', as_get=False, default='d') == 'd'

    def test_session_source(self, app):
        with app.test_request_context('/'):
            v = _View(session={'s': 'from-session'})
            assert v.get_argument_smart('s', as_session=True) == 'from-session'

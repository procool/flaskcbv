import pytest
from flaskcbv.exceptions import ConfigurationError, CSRFError
from flaskcbv.view.crud import _get_dt_s, FormMixin
from flaskcbv.forms.form import Form


class TestGetDtS:
    def test_raises_without_secret_key(self, app):
        bad_app = app.__class__(__name__)
        bad_app.config['SECRET_KEY'] = None
        with bad_app.app_context():
            with pytest.raises(ConfigurationError):
                _get_dt_s()

    def test_returns_serializer_with_secret_key(self, app_ctx):
        from itsdangerous import URLSafeTimedSerializer
        s = _get_dt_s()
        assert isinstance(s, URLSafeTimedSerializer)

    def test_serializer_uses_app_secret_key(self, app_ctx):
        ## Tokens signed with the serializer must be verifiable
        s = _get_dt_s()
        token = s.dumps('test-payload')
        payload = s.loads(token)
        assert payload == 'test-payload'


class _CsrfForm(Form):
    pass


class TestCsrfGenToken:
    def test_token_stored_in_session(self, client):
        with client.session_transaction() as sess:
            sess.clear()

        ## Access an endpoint that triggers csrf_gen_token indirectly is complex;
        ## test the method directly in a request context with session.
        with client.application.test_request_context('/'):
            from flask import session as flask_session
            ## Manually wire up a FormMixin instance for unit testing
            mixin = FormMixin()
            mixin.session = {}
            mixin.request = None
            token = mixin.csrf_gen_token(context={})
            assert 'csrf_token' in mixin.session
            assert isinstance(token, str)
            assert len(token) > 0

    def test_token_returned_as_string(self, app_ctx):
        mixin = FormMixin()
        mixin.session = {}
        mixin.request = None
        token = mixin.csrf_gen_token()
        assert isinstance(token, str)

    def test_token_idempotent_in_same_session(self, app_ctx):
        ## Calling twice with the same session should return same token
        mixin = FormMixin()
        mixin.session = {}
        mixin.request = None
        token1 = mixin.csrf_gen_token()
        token2 = mixin.csrf_gen_token()
        assert token1 == token2


class TestCsrfCheckToken:
    def _make_mixin_with_token(self):
        mixin = FormMixin()
        mixin.session = {}
        mixin.request = None
        token = mixin.csrf_gen_token()
        return mixin, token

    def test_valid_token_passes(self, app_ctx):
        mixin, token = self._make_mixin_with_token()
        form = _CsrfForm(data={'csrf_token': token})
        ## Should not raise
        mixin.csrf_check_token(form)

    def test_missing_session_token_raises(self, app_ctx):
        mixin = FormMixin()
        mixin.session = {}   ## no csrf_token in session
        mixin.request = None
        form = _CsrfForm(data={'csrf_token': 'sometoken'})
        with pytest.raises(CSRFError, match='No CSRF token'):
            mixin.csrf_check_token(form)

    def test_missing_form_field_raises(self, app_ctx):
        mixin, _ = self._make_mixin_with_token()
        form = _CsrfForm(data={})   ## no csrf_token field
        with pytest.raises(CSRFError, match='No CSRF token'):
            mixin.csrf_check_token(form)

    def test_invalid_token_raises(self, app_ctx):
        mixin, _ = self._make_mixin_with_token()
        ## Reset session so pop() doesn't find it
        mixin.session['csrf_token'] = 'expected-value'
        form = _CsrfForm(data={'csrf_token': 'completely-wrong-token'})
        with pytest.raises(CSRFError):
            mixin.csrf_check_token(form)

    def test_wrong_signature_raises_csrf_error(self, app_ctx):
        mixin, _ = self._make_mixin_with_token()
        mixin.session['csrf_token'] = 'val'
        form = _CsrfForm(data={'csrf_token': 'bad.data.here'})
        with pytest.raises(CSRFError):
            mixin.csrf_check_token(form)

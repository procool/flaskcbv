import json
import pytest
from flaskcbv.view.mixins.jsonmixin import JSONMixin
from flaskcbv.view import View


class _BaseJSONView(JSONMixin, View):
    def get_context_data(self, **kwargs):
        return {'foo': 'bar', 'baz': 42}


class TestJSONMixinEnvelope:
    def test_default_envelope_fields(self, req_ctx):
        v = _BaseJSONView()
        d = v.get_as_json_data()
        assert d['errno'] == 0
        assert d['error'] == 'Ok'
        assert d['details'] == ''

    def test_context_merged_into_response(self, req_ctx):
        v = _BaseJSONView()
        d = v.get_as_json_data()
        assert d['foo'] == 'bar'
        assert d['baz'] == 42

    def test_extra_data_kwarg_merged(self, req_ctx):
        v = _BaseJSONView()
        d = v.get_as_json_data(extra='value')
        assert d['extra'] == 'value'

    def test_get_as_json_returns_valid_json(self, req_ctx):
        v = _BaseJSONView()
        result = v.get_as_json()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


class TestJSONMixinInclude:
    def test_include_filters_to_listed_keys(self, req_ctx):
        class IncludeView(JSONMixin, View):
            def get_context_data(self, **kwargs):
                return {'a': 1, 'b': 2, 'c': 3}

            def json_response_include(self):
                return ['a', 'c']

        v = IncludeView()
        d = v.get_as_json_data()
        assert 'a' in d
        assert 'c' in d
        assert 'b' not in d

    def test_include_missing_key_silently_ignored(self, req_ctx):
        class IncludeMissingView(JSONMixin, View):
            def get_context_data(self, **kwargs):
                return {'a': 1}

            def json_response_include(self):
                return ['a', 'nonexistent']

        v = IncludeMissingView()
        d = v.get_as_json_data()
        assert 'a' in d
        assert 'nonexistent' not in d

    def test_include_none_means_all_keys(self, req_ctx):
        ## default json_response_include() returns None → all context merged
        v = _BaseJSONView()
        d = v.get_as_json_data()
        assert 'foo' in d
        assert 'baz' in d


class TestJSONMixinExclude:
    def test_default_exclude_removes_request(self, req_ctx):
        class WithRequestView(JSONMixin, View):
            def get_context_data(self, **kwargs):
                return {'request': 'should be removed', 'ok': True}

        v = WithRequestView()
        d = v.get_as_json_data()
        assert 'request' not in d
        assert d['ok'] is True

    def test_custom_exclude(self, req_ctx):
        class CustomExcludeView(JSONMixin, View):
            def get_context_data(self, **kwargs):
                return {'keep': 1, 'drop': 2}

            def json_response_exclude(self):
                return ['drop']

        v = CustomExcludeView()
        d = v.get_as_json_data()
        assert 'keep' in d
        assert 'drop' not in d

    def test_exclude_missing_key_ignored(self, req_ctx):
        class ExcludeMissingView(JSONMixin, View):
            def json_response_exclude(self):
                return ['no_such_key']

        v = ExcludeMissingView()
        ## should not raise
        v.get_as_json_data()


class TestJSONMixinError:
    def test_json_error_default_fields(self, req_ctx):
        v = _BaseJSONView()
        result = json.loads(v.json_error())
        assert result['errno'] == -1
        assert result['error'] == 'Failed'
        assert result['details'] == ''

    def test_json_error_custom_fields(self, req_ctx):
        v = _BaseJSONView()
        result = json.loads(v.json_error(errno=-2, error='Not found', details='missing'))
        assert result['errno'] == -2
        assert result['error'] == 'Not found'
        assert result['details'] == 'missing'

    def test_context_exception_returns_error_envelope(self, req_ctx):
        class BrokenView(JSONMixin, View):
            def get_context_data(self, **kwargs):
                raise ValueError('boom')

        v = BrokenView()
        d = v.get_as_json_data()
        assert d['errno'] == -1
        assert 'boom' in d['details']

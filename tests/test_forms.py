import pytest
from flaskcbv.forms.form import Form


class SimpleForm(Form):
    def clean_name(self, value):
        if not value:
            raise ValueError('name is required')
        return value.strip()

    def clean_age(self, value):
        age = int(value)
        if age < 0:
            raise ValueError('age must be positive')
        return age


class TestFormInit:
    def test_empty_data(self):
        f = Form()
        assert f.data == {}
        assert f.errors == {}
        assert f.cleaned_data == {}

    def test_data_copied_from_raw(self):
        raw = {'foo': 'bar', 'baz': '42'}
        f = Form(data=raw)
        assert f.data == raw
        ## data is a shallow copy, not the original dict
        assert f.data is not raw

    def test_immutable_multi_dict_compatible(self):
        ## Werkzeug ImmutableMultiDict iterates keys — verify Form handles it
        from werkzeug.datastructures import ImmutableMultiDict
        imd = ImmutableMultiDict([('x', '1'), ('y', '2')])
        f = Form(data=imd)
        assert f.data['x'] == '1'
        assert f.data['y'] == '2'


class TestFormValidation:
    def test_valid_data(self):
        f = SimpleForm(data={'name': 'Alice', 'age': '30'})
        assert f.validate() is True
        assert f.cleaned_data['name'] == 'Alice'
        assert f.cleaned_data['age'] == 30
        assert f.errors == {}

    def test_invalid_empty_name(self):
        f = SimpleForm(data={'name': '', 'age': '25'})
        assert f.validate() is False
        assert 'name' in f.errors

    def test_invalid_age(self):
        f = SimpleForm(data={'name': 'Bob', 'age': '-5'})
        assert f.validate() is False
        assert 'age' in f.errors

    def test_missing_field_set_to_none(self):
        ## Fields with clean_ method but absent from data are set to None
        f = SimpleForm(data={'age': '20'})
        f.validate()
        assert 'name' in f.errors

    def test_fields_without_clean_copied_to_cleaned_data(self):
        f = Form(data={'extra': 'value'})
        f.validate()
        assert f.cleaned_data['extra'] == 'value'

    def test_is_clean_true(self):
        f = SimpleForm(data={'name': 'Alice', 'age': '30'})
        f.validate()
        assert f.is_clean is True

    def test_is_clean_false(self):
        f = SimpleForm(data={'name': '', 'age': '30'})
        f.validate()
        assert f.is_clean is False

    def test_multiple_errors(self):
        f = SimpleForm(data={'name': '', 'age': '-1'})
        f.validate()
        assert len(f.errors) == 2

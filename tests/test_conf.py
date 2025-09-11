import os
import pytest
from flaskcbv.conf import settings
from flaskcbv.conf.defaults import DefaultSettings


class TestDefaultSettings:
    def test_has_template_path(self):
        d = DefaultSettings()
        assert hasattr(d, 'TEMPLATE_PATH')

    def test_has_static_path(self):
        d = DefaultSettings()
        assert hasattr(d, 'STATIC_PATH')

    def test_has_static_url(self):
        d = DefaultSettings()
        assert hasattr(d, 'STATIC_URL')

    def test_has_default_headers(self):
        d = DefaultSettings()
        assert hasattr(d, 'DEFAULT_HEADERS')
        assert isinstance(d.DEFAULT_HEADERS, dict)


class TestSettings:
    def test_settings_module_attribute_set(self):
        ## settings was instantiated with FLASK_SETTINGS_MODULE=settings
        assert settings.SETTINGS_MODULE == 'settings'

    def test_reads_values_from_module(self):
        ## tests/settings.py defines STATIC_URL = '/static'
        assert settings.STATIC_URL == '/static'

    def test_default_values_applied(self):
        ## DEFAULT_HEADERS is defined both in defaults and in test settings
        assert isinstance(settings.DEFAULT_HEADERS, dict)

    def test_settings_raises_without_env_var(self, monkeypatch):
        monkeypatch.delenv('FLASK_SETTINGS_MODULE', raising=False)
        from flaskcbv.conf import Settings
        with pytest.raises(KeyError):
            Settings()

    def test_settings_raises_on_bad_module(self, monkeypatch):
        monkeypatch.setenv('FLASK_SETTINGS_MODULE', 'nonexistent_module_xyz')
        from flaskcbv.conf import Settings
        with pytest.raises(ImportError):
            Settings()

"""Tests for CBVCore.make_urls() namespaces/namespases dual-support (2.3.x)."""
import sys
import types

import pytest

from flaskcbv.core import CBVCore
from flaskcbv.url import Url, make_urls
from flaskcbv.view import View
from flaskcbv.response import Response


class _V(View):
    def get(self, request, *args, **kwargs):
        return Response('x')


class _StubApp:
    """Minimal stand-in for the Flask app: records add_url_rule() calls."""
    def __init__(self):
        self.rules = []

    def add_url_rule(self, *args, **kwargs):
        self.rules.append((args, kwargs))


def _fake_urls_module(**attrs):
    mod = types.ModuleType('urls')
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _run_make_urls(monkeypatch, urls_module):
    ## Make importlib.import_module('urls') return our fake module.
    monkeypatch.setitem(sys.modules, 'urls', urls_module)
    ## Bypass __init__ (which builds a real Flask app); exercise make_urls only.
    core = CBVCore.__new__(CBVCore)
    core.app = _StubApp()
    core.make_urls()
    return core


def _url_table():
    return make_urls(Url('/a', _V(), name='a'))


def test_accepts_new_namespaces(monkeypatch):
    core = _run_make_urls(monkeypatch, _fake_urls_module(namespaces=_url_table()))
    assert len(core.app.rules) == 1


def test_accepts_deprecated_namespases_with_warning(monkeypatch):
    with pytest.warns(DeprecationWarning):
        core = _run_make_urls(monkeypatch, _fake_urls_module(namespases=_url_table()))
    assert len(core.app.rules) == 1


def test_prefers_namespaces_over_namespases(monkeypatch):
    ## When both are present, the new name wins and no warning is emitted.
    import warnings
    table = _url_table()
    with warnings.catch_warnings():
        warnings.simplefilter('error')  # any DeprecationWarning would fail
        core = _run_make_urls(
            monkeypatch,
            _fake_urls_module(namespaces=table, namespases=_url_table()),
        )
    assert len(core.app.rules) == 1


def test_raises_when_neither_defined(monkeypatch):
    with pytest.raises(Exception):
        _run_make_urls(monkeypatch, _fake_urls_module())

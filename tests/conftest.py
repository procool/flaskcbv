import os
import sys

## Must happen before any flaskcbv import:
## CBVCore.make_urls() does bare 'from urls import namespases'
sys.path.insert(0, os.path.dirname(__file__))
## flaskcbv.conf.Settings() reads this at import time
os.environ.setdefault('FLASK_SETTINGS_MODULE', 'settings')

import pytest
import flaskcbv.core.base as _core_base
from flaskcbv.core import create_engine


@pytest.fixture(scope='session')
def engine():
    ## Single engine for the whole test session — avoids duplicate
    ## endpoint registration errors when Flask app is re-created.
    _core_base.flask_[0] = None
    return create_engine()


@pytest.fixture(scope='session')
def app(engine):
    engine.app.config.update({
        'TESTING':    True,
        'SECRET_KEY': 'test-secret-key-for-pytest',
    })
    return engine.app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield app


@pytest.fixture
def req_ctx(app):
    with app.test_request_context():
        yield app

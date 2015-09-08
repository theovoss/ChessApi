import pytest
import sqlalchemy_utils

from .utilities import db_drop_everything
from api.database import db as _db
from api.settings import TestConfig
from api.app import create_app


def pytest_configure(config):
    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False
    terminal.TerminalReporter = QuietReporter


@pytest.yield_fixture
def app():
    _app = create_app(TestConfig)
    _app.testing = True
    _app.debug = True

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.yield_fixture
def db(app):
    url = app.config['SQLALCHEMY_DATABASE_URI']
    if not sqlalchemy_utils.database_exists(url):
        sqlalchemy_utils.create_database(url)

    db_drop_everything(_db)
    _db.create_all()

    yield _db

    _db.session.close()
    db_drop_everything(_db)

#!flask/bin/python
from flask import Flask
from sqlalchemy_utils import database_exists, create_database

from .routes import blueprint as routes_blueprint
from .database import db, migrate
from .settings import ProdConfig


def create_app(config_object=ProdConfig, _db=db):
    app = Flask(__name__, static_url_path="")
    app.config.from_object(config_object)
    register_extensions(app, _db)
    register_blueprints(app)
    return app


def register_extensions(app, _db):
    if _db is not None:
        url = app.config['SQLALCHEMY_DATABASE_URI']
        if not database_exists(url):
            create_database(url)
        _db.app = app
        _db.init_app(app)
        with app.app_context():
            _db.create_all()
        migrate.init_app(app, _db)


def register_blueprints(app):
    app.register_blueprint(routes_blueprint)

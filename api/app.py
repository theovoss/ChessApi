#!flask/bin/python
import base64

from flask import Flask
from sqlalchemy_utils import database_exists, create_database
from flask.ext.login import LoginManager, login_user, logout_user, \
    login_required, current_user

from .routes import blueprint as routes_blueprint
from .database import db, migrate, User
from .settings import ProdConfig


def create_app(config_object=ProdConfig, _db=db):
    app = Flask(__name__, static_url_path="")

    # Principal(app)

    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(userid):
        # Return an instance of the User model
        return User.get(id=userid)

    @login_manager.request_loader
    def request_loader(request):
        return load_user_from_request(request)

    app.config.from_object(config_object)
    register_extensions(app, _db)
    register_blueprints(app)
    return app


def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        key = api_key.decode("utf-8")
        email, password = key.split(':')
        print("Email: {}, Password: {}".format(email, password))
        user = User.query.filter_by(email=email).first()
        print("have user")
        print(user)
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


def register_extensions(app, _db):
    _db.app = app
    _db.init_app(app)
    migrate.init_app(app, _db)


def register_blueprints(app):
    app.register_blueprint(routes_blueprint)

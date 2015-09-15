# -*- coding: utf-8 -*-
import os
import getpass

os_env = os.environ
name = getpass.getuser()


class Config(object):
    SECRET_KEY = "stupid_secret_key"
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://{}@localhost/chess_api_prod'.format(name)
    )


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}@localhost/chess_api_dev'.format(name)


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{}@localhost/chess_api_test'.format(name)

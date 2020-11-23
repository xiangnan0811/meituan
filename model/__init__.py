# config=utf-8
from flask import Flask
from flask_login import LoginManager
from common import db

login_manager = LoginManager()


login_manager.login_view = "user.login"


def create_app(config_filename=None):
    app = Flask(__name__)
    login_manager.init_app(app)

    if config_filename is not None:
        app.config.from_pyfile(config_filename)
        configure_database(app)

    return app


def configure_database(app):
    db.init_app(app)

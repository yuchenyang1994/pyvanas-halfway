# -*- coding: utf-8 -*-
from flask import Flask
from flask import request,redirect,url_for,render_template
from werkzeug.contrib.fixers import ProxyFix

from modules.vanas_app.vanas_view import vanas
from config import BaseConfig
from extensions import mongo,redis_store,socketio
from logger import configure_app_logger

__all__ = ['create_app']

def create_app(config=None,app_name=None):
    """create app

    :config: TODO
    :app_name: TODO
    :returns: TODO

    """
    if app_name is None:
        app_name = BaseConfig.PROJECT
    app = Flask(__name__,instance_relative_config=True)
    configure_app(app)
    configure_extensions(app)
    configure_blueprints(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    return app

def configure_blueprints(app):
    """Configure blueprints in views.
        TODO:takethis
    """
    # register_blue_point
    app.register_blueprint(vanas,url_prefix='/vanas')

    # entiy
    @app.route('/')
    def index():
        return 'hello,world'


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(BaseConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)

def configure_extensions(app):
    """plugin

    :app: TODO
    :returns: TODO

    """
    # Mongo
    mongo.init_app(app)
    # redis
    redis_store.init_app(app)
    # socketio
    socketio.init_app(app)

def configure_template_filters(app):

    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)

def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    # Config Logger
    configure_app_logger(app)


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500





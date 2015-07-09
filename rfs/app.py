import os
import datetime
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle

from rfs.config import DefaultConfig

db = SQLAlchemy()
assets = Environment()

from products.views import products
DEFAULT_BLUEPRINTS = (
    products,
)

def create_app(config=None, app_name=None, blueprints=None):
    """
    Create and configure the Flask app
    """
    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS
    app = Flask(app_name,
                static_url_path='',
                instance_relative_config=True
               )
    configure_app(app, config)
    configure_template_processors(app)
    configure_blueprints(app, blueprints)
    configure_logging(app)
    configure_error_handlers(app)
    configure_database(app)
    configure_assets(app)
    
    return app

def configure_app(app, config=None):
    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    if config is not None:
        app.config.from_object(config)

def configure_logging(app):

    if app.debug or app.testing:
        app.logger.setLevel(logging.DEBUG)
        # Skip debug and test mode. Just check standard output.
        return

    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'shop.log')
    info_file_handler = RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)


def configure_template_processors(app):

    @app.context_processor
    def my_processors():
        def now(format="%d-%m-%d %H:%M:%S"):
            return datetime.datetime.now().strftime(format)

        return dict(now=now)

def configure_blueprints(app, blueprints):

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_error_handlers(app):

    @app.errorhandler(403)
    @app.errorhandler(401)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500

def configure_database(app):
    db.init_app(app)

def configure_assets(app):
    assets.init_app(app)
    js = Bundle("libs/react/react.js",
                "libs/jquery/dist/jquery.js",
                "libs/bootstrap/dist/js/bootstrap.min.js",
                filters="jsmin", output="libs/bundle.js")
    assets.register("js_all",js)

    import jsx
    jsx = Bundle("jsx/app.js",
                 filters="jsx", output="js/app.js")
    assets.register("jsx_all",jsx)
    
    css = Bundle("libs/bootstrap/dist/css/bootstrap.css",
                 "css/app.css",
                 filters="cssmin",
                 output="libs/bundle.css")
    assets.register("css_all",css)
    
    
    
                 
    
                
import logging

from werkzeug.exceptions import HTTPException
from werkzeug.contrib.fixers import ProxyFix

from flask import Flask
from flask.logging import default_handler

from flask_cors import CORS
from flask_jwt_extended import JWTManager

from flaskapp import settings
from flaskapp.core.util import app_exception_handler


def create_app():
    app = Flask(__name__, instance_path='/opt/flaskapp-instance')

    # Pull in app settings
    app.config.from_object(settings)

    # Configure logging
    default_handler.setLevel(
        logging.DEBUG if app.debug else app.config['PROD_LOG_LEVEL'])

    app.logger.setLevel(logging.DEBUG)

    # Apply Werkzeug middleware so Flask can correctly deduce
    # the client request environment when behind a proxy
    if (app.config['UPSTREAM_PROXY_COUNT'] > 0):
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            app.config['UPSTREAM_PROXY_COUNT'])

    # Setup the Flask-JWT-Extended extension
    if app.debug:
        jwt_pub_key_file = '.jwt/dummy/pubkey.pem'
    else:
        jwt_pub_key_file = '.jwt/pubkey.pem'

    with app.open_instance_resource(jwt_pub_key_file) as f:
        app.config['JWT_PUBLIC_KEY'] = f.read()

    JWTManager(app)

    # Allow cross origin requests on all endpoints (they will
    # still need to present a valid JWT to gain access)
    CORS(app)

    # Import views
    from flaskapp.views import auth
    from flaskapp.views.api_v1 import manage
    from flaskapp.views.api_v1 import devices
    from flaskapp.views.api_v1 import station
    from flaskapp.views.api_v1 import home

    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(manage.bp, url_prefix='/api/v1/manage')
    app.register_blueprint(devices.bp, url_prefix='/api/v1/devices')
    app.register_blueprint(station.bp, url_prefix='/api/v1/station')
    app.register_blueprint(home.bp, url_prefix='/api/v1/home')

    # Register app level error handlers
    app.register_error_handler(HTTPException, app_exception_handler)

    # Set final actions on outgoing responses
    @app.after_request
    def perform_exit_actions(response):
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('X-XSS-Protection', '1; mode=block')

        return response

    return app

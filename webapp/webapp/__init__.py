import os
import logging

from werkzeug.exceptions import HTTPException
from flask import Flask, request
from flask_cors import CORS

from webapp import settings
from webapp.core.error import app_exception_handler

class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)

def create_app():
    # Instantiate app
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Pull in configuration
    app.config.from_object(settings)

    # Set up logging (TO DO: add alternative, non-stream based, logging for prod)
    formatter = RequestFormatter(
        "%(asctime)s %(remote_addr)s: requested %(url)s: %(levelname)s "
        "in [%(module)s: %(lineno)d]: %(message)s"
    )

    strm = logging.StreamHandler()
    strm.setLevel(logging.DEBUG if app.debug else logging.WARNING)
    strm.setFormatter(formatter)

    app.logger.addHandler(strm)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.WARNING)

    root = logging.getLogger("core")
    root.addHandler(strm)

    # Import views
    from webapp.views import main
    from webapp.views import api_v1

    # Register blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(api_v1.bp, url_prefix='/api/v1')

    # Register app level error handlers
    app.register_error_handler(HTTPException, app_exception_handler)

    # Setup final actions to be applied against outgoing responses
    @app.after_request
    def perform_exit_actions(response):
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('X-XSS-Protection', '1; mode=block')

        return response

    return app

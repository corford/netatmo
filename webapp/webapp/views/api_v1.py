from werkzeug.exceptions import HTTPException

from flask import Blueprint
from flask import current_app as app

from webapp.core.error import WebappApiUsageError, api_exception_handler
from webapp.core.util import create_api_response

bp = Blueprint("api_v1", __name__)  

bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(WebappApiUsageError, api_exception_handler)

@bp.route("/test/", methods=["GET"])
def test():
    return create_api_response(message="test")

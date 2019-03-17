from werkzeug.exceptions import HTTPException

from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskapp.core.exceptions import FlaskappApiError

from flaskapp.core.util import (
    create_api_response,
    api_exception_handler
)

from flaskapp.models.user import User

bp = Blueprint('manage', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(FlaskappApiError, api_exception_handler)


@bp.route('/revoke', methods=['GET'])
@jwt_required
def revoke():
    user = User(get_jwt_identity())
    user.delete('auth_token', auto_commit=False)
    user.delete('refresh_token', auto_commit=False)
    user.save()

    return create_api_response(
        message='netatmo account access revoked'
    )

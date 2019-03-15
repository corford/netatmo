import requests
from werkzeug.exceptions import HTTPException

from flask import current_app as app
from flask import request as r
from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskapp.core.error import WebappApiUsageError, api_exception_handler
from flaskapp.core.util import create_api_response

from flaskapp.models.user import User

bp = Blueprint('home_v1', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(WebappApiUsageError, api_exception_handler)


# TO DO: make this view's logic more dry by taking it out of
# the view and putting it in to a view specific model/class
@bp.route('/timezone', methods=['GET'])
@jwt_required
def timezone():
    user = User(get_jwt_identity())
    home_id = r.args.get('home_id', default=None, type=str)

    if home_id is None:
        return create_api_response(
            message='home_id required',
            status=400
            )

    else:
        endpoint = 'https://api.netatmo.com/api/homesdata'
        payload = {
            'access_token': user.get('access_token'),
            'home_id': home_id
        }

        # Get home
        try:
            response = requests.get(endpoint, params=payload)
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            app.logger.info(
                'Error while requesting netatmo home '
                '(%s) data for user %s: %s (%s)',
                home_id,
                user.id,
                err.response.text,
                err.response.status_code)

            return create_api_response(
                message=err.response.text,
                status=err.response.status_code
                )

        try:
            timezone = response.json()['body']['homes'][0]['timezone']

        except KeyError:
            return create_api_response(
                message=f'problem parsing response from {endpoint}',
                status=500)

        return create_api_response(message=timezone)

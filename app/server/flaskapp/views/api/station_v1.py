import requests
from werkzeug.exceptions import HTTPException

from flask import current_app as app
from flask import request as r
from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskapp.core.error import WebappApiUsageError, api_exception_handler
from flaskapp.core.util import create_api_response

from flaskapp.models.user import User

bp = Blueprint('station_v1', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(WebappApiUsageError, api_exception_handler)


# TO DO: make this view's logic more dry by taking it out of
# the view and putting it in to a view specific model/class
@bp.route('/dashboard-data', methods=['GET'])
@jwt_required
def data():
    user = User(get_jwt_identity())
    device_id = r.args.get('device_id', default=None, type=str)

    if device_id is None:
        return create_api_response(
            message='device_id required',
            status=400
            )

    else:
        endpoint = 'https://api.netatmo.com/api/getstationsdata'
        payload = {
            'access_token': user.get('access_token'),
            'device_id': device_id
        }

        # Get station
        try:
            response = requests.get(endpoint, params=payload)
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            app.logger.info(
                'Error while requesting netatmo station '
                '(%s) data for user %s: %s (%s)',
                device_id,
                user.id,
                err.response.text,
                err.response.status_code)

            return create_api_response(
                message=err.response.text,
                status=err.response.status_code
                )

        try:
            dashboard_data = \
                response.json()['body']['devices'][0]['dashboard_data']

        except KeyError:
            return create_api_response(
                message=f'problem parsing response from {endpoint}',
                status=500)

        return create_api_response(
            message='dashboard_data',
            data=dashboard_data
            )

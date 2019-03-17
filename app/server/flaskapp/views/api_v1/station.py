import requests
from werkzeug.exceptions import HTTPException

from flask import current_app as app
from flask import request as request
from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskapp.core.exceptions import (
    FlaskappApiError,
    FlaskappNetatmoTokenRefreshError
)

from flaskapp.core.util import (
    create_api_response,
    api_exception_handler,
    SmartRequest
)

from flaskapp.models.user import User

bp = Blueprint('station', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(FlaskappApiError, api_exception_handler)


@bp.route('/dashboard-data', methods=['GET'])
@jwt_required
def dashboard_data():
    user = User(get_jwt_identity())
    device_id = request.args.get('device_id', default=None, type=str)

    if device_id is None:
        raise FlaskappApiError(
            message='device_id required',
            code=400
        )

    # Get station dash data
    else:
        endpoint = 'https://api.netatmo.com/api/getstationsdata'
        payload = {
            'access_token': user.get('access_token'),
            'device_id': device_id
        }

        try:
            r = requests.Request('GET', endpoint, params=payload)
            sr = SmartRequest()
            response = sr.query(user, r.prepare(), timeout=5)

        except (requests.exceptions.HTTPError,
                FlaskappNetatmoTokenRefreshError) as err:

            app.logger.info(
                'Error requesting netatmo station (device id: %s) '
                'dash data for user %s: %s (%s)',
                device_id,
                user.id,
                err.response.text,
                err.response.status_code
            )

            raise FlaskappApiError(
                message='error requesting netatmo station dash data',
                code=500
            )

        try:
            dashboard_data = \
                response.json()['body']['devices'][0]['dashboard_data']

        except (TypeError, KeyError, ValueError) as err:
            app.logger.error(
                'Error parsing response from netatmo endpoint %s: %s',
                endpoint,
                err
            )

            raise FlaskappApiError(
                message='error processing netatmo station dash data',
                code=500
            )

        return create_api_response(
            message='dashboard_data',
            data=dashboard_data
        )

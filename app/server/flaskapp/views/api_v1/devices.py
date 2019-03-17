import requests
from werkzeug.exceptions import HTTPException

from flask import current_app as app
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

bp = Blueprint('devices', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(FlaskappApiError, api_exception_handler)


@bp.route('/list', methods=['GET'])
@jwt_required
def list_devices():
    user = User(get_jwt_identity())

    endpoint = {
        'station': 'https://api.netatmo.com/api/getstationsdata',
        'home': 'https://api.netatmo.com/api/homesdata'
    }

    payload = {
        'access_token':
        user.get('access_token')
    }

    result = []

    # Get stations
    try:
        r = requests.Request('GET', endpoint['station'], params=payload)
        sr = SmartRequest()
        response = sr.query(user, r.prepare(), timeout=5)

    except (requests.exceptions.HTTPError,
            FlaskappNetatmoTokenRefreshError) as err:

        app.logger.info(
            'Error requesting netatmo station devices for user %s: %s (%s)',
            user.id,
            err.response.text,
            err.response.status_code)

        raise FlaskappApiError(
            message='error requesting netatmo station devices',
            code=500
        )

    try:
        for device in response.json()['body']['devices']:
            result.append({
                'id': device['_id'],
                'type': device['type']
            })

    except (TypeError, KeyError, ValueError) as err:
        app.logger.error(
            'Error parsing response from netatmo endpoint %s: %s',
            endpoint['station'],
            err
        )

        raise FlaskappApiError(
            message='error processing netatmo station devices',
            code=500
        )

    # Get home devices
    try:
        r = requests.Request('GET', endpoint['home'], params=payload)
        sr = SmartRequest()
        response = sr.query(user, r.prepare(), timeout=5)

    except (requests.exceptions.HTTPError,
            FlaskappNetatmoTokenRefreshError) as err:

        app.logger.info(
            'Error getting netatmo home devices for user %s: %s (%s)',
            user.id,
            err.response.text,
            err.response.status_code)

        raise FlaskappApiError(
            message='error requesting netatmo home devices',
            code=500
        )

    try:
        for home in response.json()['body']['homes']:
            for device in home['modules']:
                result.append({
                    'id': device['id'],
                    'type': device['type'],
                    'home_id': home['id']
                })

    except (TypeError, KeyError, ValueError) as err:
        app.logger.error(
            'Error parsing response from netatmo endpoint %s: %s',
            endpoint['home'],
            err
        )

        raise FlaskappApiError(
            message='error processing netatmo home devices',
            code=500
        )

    return create_api_response(message='', data={'devices': result})

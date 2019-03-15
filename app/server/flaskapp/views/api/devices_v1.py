import requests
from werkzeug.exceptions import HTTPException

from flask import current_app as app
from flask import Blueprint

from flask_jwt_extended import jwt_required, get_jwt_identity

from flaskapp.core.error import WebappApiUsageError, api_exception_handler
from flaskapp.core.util import create_api_response

from flaskapp.models.user import User

bp = Blueprint('devices_v1', __name__)

# Register error API tailored handlers
bp.register_error_handler(HTTPException, api_exception_handler)
bp.register_error_handler(WebappApiUsageError, api_exception_handler)


# TO DO: make this view's logic more dry by taking it out of
# the view and putting it in to a view specific model/class
@bp.route('/list', methods=['GET'])
@jwt_required
def devices():
    user = User(get_jwt_identity())
    payload = {'access_token': user.get('access_token')}
    stations_endpoint = 'https://api.netatmo.com/api/getstationsdata'
    homes_endpoint = 'https://api.netatmo.com/api/homesdata'
    devices = {
        'stations': [],
        'homes': {}
    }

    # Get stations
    try:
        response = requests.get(stations_endpoint, params=payload)
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        app.logger.info(
            'Error while requesting netatmo station '
            'devices for user %s: %s (%s)',
            user.id,
            err.response.text,
            err.response.status_code)

        return create_api_response(
            message=err.response.text,
            status=err.response.status_code)

    try:
        for device in response.json()['body']['devices']:
            devices['stations'].append(device)

    except KeyError:
        return create_api_response(
            message=f'problem parsing response from {stations_endpoint}',
            status=500)

    # Get home devices
    try:
        response = requests.get(homes_endpoint, params=payload)
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        app.logger.info(
            'Error while requesting netatmo home devices for user %s: %s (%s)',
            user.id,
            err.response.text,
            err.response.status_code)

        return create_api_response(
            message=err.response.text,
            status=err.response.status_code)

    try:
        for home in response.json()['body']['homes']:
            devices['homes'][home['id']] = []
            for device in home['modules']:
                devices['homes'][home['id']].append(device)

    except KeyError:
        return create_api_response(
            message=f'problem parsing response from {homes_endpoint}',
            status=500)

    return create_api_response(message='devices', data=devices)

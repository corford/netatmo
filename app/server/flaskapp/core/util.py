import requests

from werkzeug.exceptions import HTTPException

from flask import current_app as app
from flask import jsonify

from flaskapp.core.exceptions import (
    FlaskappApiError,
    FlaskappNetatmoTokenRefreshError
)


def is_int(val):
    try:
        int(val)
    except (TypeError, ValueError):
        return False

    return True


def api_exception_handler(err):
    code = 500
    if isinstance(err, HTTPException) \
            or isinstance(err, FlaskappApiError):
        code = err.code

    return create_api_response(message=err.message, status=code)


def app_exception_handler(err):
    code = err.code if isinstance(err, HTTPException) else 500
    message = (
        f'<h1>Sorry, something went wrong (code: {code})</h1>'
        f'<p>We\'ve logged the error and our team will look at it</p>'
    )

    return message, code


def create_api_response(data=None, status=200, message=''):
    if type(data) is not dict and data is not None:
        raise TypeError('Data should be a dictionary')

    if not is_int(status):
        raise TypeError('Status should be an integer')

    success = True if status >= 200 and status < 300 else False
    response = {'success': success, 'message': message, 'result': data}

    return jsonify(response), status


class SmartRequest(object):
    ''' Requests to Netatmo API endpoints made through this helper
    class automatically handle access token refreshes for you
    '''

    def query(self, user, query, timeout=5):
        refresh_access_token = False

        with requests.Session() as session:
            response = session.send(
                query,
                timeout=timeout
            )

            # If we get a 403, check if access token needs refreshing
            if response.status_code == 403:
                try:
                    if response.json()['error']['code'] == 3:
                        app.logger.info(
                            'netatmo access token for user %s has expired',
                            self._user.id
                        )

                        refresh_access_token = True

                except (TypeError, KeyError, ValueError):
                    pass

                if refresh_access_token \
                        and self._refresh_access_token(user, timeout):

                    # Re-run original request using new access token
                    response = session.send(
                        query,
                        timeout=timeout
                    )

            response.raise_for_status()
            return response

    def _refresh_access_token(self, user, timeout):
        try:
            app.logger.info(
                'Refreshing netatmo access token for user: %s', user.id)

            endpoint = 'https://api.netatmo.com/oauth2/token'
            payload = {
                'grant_type': 'authorization_code',
                'client_id': app.config['NETATMO_CLIENT_ID'],
                'client_secret': app.config['NETATMO_CLIENT_SECRET'],
                'refresh_token': user.get(
                    'refresh_token',
                    raise_on_missing=True
                )
            }

            response = requests.post(endpoint, data=payload, timeout=timeout)
            response.raise_for_status()

            user.set('access_token', response.json()['access_token'])

        except Exception as err:
            app.logger.warning(
                'Error refreshing netatmo access token: %s', err)

            raise FlaskappNetatmoTokenRefreshError(
                    'error refreshing netatmo access token')

        return True

    def __repr__(self):
        return fr'<{self.__class__.__name__}({self._user})>'

    def __str__(self):
        return self.__class__.__name__

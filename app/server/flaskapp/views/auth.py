import requests
import uuid

from flask import current_app as app
from flask import redirect
from flask import request as r
from flask import Blueprint
from flask import make_response

from flask_jwt_extended import jwt_optional, get_jwt_identity

from flaskapp.models.user import User

bp = Blueprint('auth', __name__)


@bp.route('/grant', methods=['GET'])
@jwt_optional
def grant():
    authT_endpoint = 'https://api.netatmo.com/oauth2/authorize'
    authZ_endpoint = 'https://api.netatmo.com/oauth2/token'

    # Look for JWT token
    jwt_identity = get_jwt_identity()
    if jwt_identity is not None:
        user = User(jwt_identity)

    # Look for cookie (available after redirect back from Netatmo)
    elif 'jwt_identity' in r.cookies:
        user = User(r.cookies['jwt_identity'])

    # Bail (either user wrongly called this endpoint without a JWT or
    # the cookie expired before Netatmo redirected back here)
    else:
        return ('<h1>Error: we could not identify you</h1>')

    app.logger.debug(
        'Handling Netatmo account grant flow for user: %s',
        user.id)

    # User declined to grant access to their Netatmo account
    if r.args.get('error') == 'access_denied':
        return ('<h1>Error: you chose not to grant access to your Netatmo '
                'account</h1>')

    # Netatmo API replied with an error (most likely due to malformed
    # or missing url params)
    elif r.args.get('error'):
        return ('<h1>Uh-oh. An error occurred while calling the '
                'Netatmo API (%s). Sorry.</h1>', r.args.get('error'))

    # User has authenticated with Netatmo and granted access to their account.
    # Now we need to ollect the access and refresh tokens.
    elif r.args.get('code') and user.get('refresh_token') is None:
        if r.args.get('state') == user.get('csrf'):
            code = r.args.get('code')
            payload = {
                'grant_type': 'authorization_code',
                'client_id': app.config['NETATMO_CLIENT_ID'],
                'client_secret': app.config['NETATMO_CLIENT_SECRET'],
                'code': code,
                'redirect_uri': f'{r.host_url}auth/grant',
                'scope': ' '.join(app.config['NETATMO_SCOPES'])
                }
            try:
                response = requests.post(authZ_endpoint, data=payload)
                response.raise_for_status()

                user.set(
                    'access_token',
                    response.json()['access_token'],
                    auto_commit=False)

                user.set(
                    'refresh_token',
                    response.json()['refresh_token'],
                    auto_commit=False)

                user.set(
                    'scope',
                    response.json()['scope'],
                    auto_commit=False)

                user.save()

                return ('<h1>Success! You have granted us access to your '
                        'Netatmo account (you may now close this window)</h1>')

            except requests.exceptions.HTTPError as err:
                app.logger.info(
                    'Error while requesting netatmo tokens for user: %s (%s)',
                    err.response.text,
                    err.response.status_code)
                return ('<h1>Uh-oh. An error occurred while accessing '
                        'your Netatmo account. Sorry.</h1>')
        else:
            return '<h1>Request ignored (invalid state)</h1>'

    # Begin the authentication flow if user has not already granted
    # us access to their Netatmo account
    elif user.get('refresh_token') is None:
        payload = {
          'client_id': app.config['NETATMO_CLIENT_ID'],
          'redirect_uri': f'{r.host_url}auth/grant',
          'scope': ' '.join(app.config['NETATMO_SCOPES']),
          'state': str(uuid.uuid4())
          }

        user.set('csrf', payload['state'])

        try:
            response = requests.post(authT_endpoint, params=payload)
            response.raise_for_status()

            # Set a short lived cookie so we can identify the user when they
            # get redirected back after authenticating with Netatmo
            resp = make_response(redirect(response.url, code=302))
            resp.set_cookie('jwt_identity', user.id, max_age=90, httponly=True)
            return resp

        except requests.exceptions.HTTPError:
            return ('<h1>Uh-oh. An error occurred while attempting '
                    'to authenticate with Netatmo. Sorry.</h1>')

    # Do nothing (user has already granted access to their Netatmo acount)
    else:
        return ('<h1>Hmmm. You have already granted us access '
                'to your Netatmo account.</h1>')

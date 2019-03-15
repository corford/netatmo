import os
import logging

from dotenv import load_dotenv
from pathlib import Path

# Pull in sensitive settings via an .env file
env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

# Get secret key for signing cookies
SECRET_KEY = os.environ.get('SECRET_KEY', default=None)
if not SECRET_KEY:
    raise RuntimeError('No secret key set for Flask application')

# Netatmo vars
NETATMO_CLIENT_ID = os.environ.get('NETATMO_CLIENT_ID', default=None)
NETATMO_CLIENT_SECRET = os.environ.get('NETATMO_CLIENT_SECRET', default=None)
if not NETATMO_CLIENT_ID or not NETATMO_CLIENT_SECRET:
    raise RuntimeError('Missing Netatmo API configuration')

NETATMO_SCOPES = ['read_station', 'read_thermostat']

# Flask-JWT-Extended setup
JWT_ALGORITHM = 'RS256'
JWT_DECODE_AUDIENCE = 'server:flaskapp'
JWT_IDENTITY_CLAIM = 'sub'
JWT_TOKEN_LOCATION = ['headers', 'query_string']

# Effective log level for prod env (defaults to 'INFO')
PROD_LOG_LEVEL = os.environ.get('PROD_LOG_LEVEL', default=logging.INFO)

'''
Where to persist user data (like netatmo refresh and auth tokens).
At the moment only Redis is supported but additional storage plugins
can easily be written later e.g. for postgres/mysql/mongodb)
'''
STORAGE_PLUGIN = os.environ.get('STORAGE_PLUGIN', default='redis')
STORAGE_HOST = os.environ.get('STORAGE_HOST', default='127.0.0.1')
STORAGE_PORT = os.environ.get('STORAGE_PORT', default=6379)
STORAGE_DB = os.environ.get('STORAGE_DB', default=0)
STORAGE_USER = os.environ.get('STORAGE_USER', default=None)
STORAGE_PWD = os.environ.get('STORAGE_PWD', default=None)

'''
If Flask is sitting behind one or more http proxies/ssl terminators
(e.g. haproxy/elb/nginx), set the number of upstream proxies it is safe
to deduce the original client request environment from.

IMPORTANT: client's can set whatever headers they like, so it is
essential we only trust headers set by upstream proxies under our
control. For more info, consult the Werkzeug ProxyFix source code.

The default assumes 1 proxy will be in front of our prod Flask app (since
exposing gunicorn or uwsgi directly to the web is unusual)
'''
UPSTREAM_PROXY_COUNT = int(os.environ.get('UPSTREAM_PROXY_COUNT', default=1))

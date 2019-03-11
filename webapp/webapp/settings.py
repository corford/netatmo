import os

SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
if not SECRET_KEY:
    raise RuntimeError("No secret key set for Flask application")

STORAGE_BACKEND=os.environ.get("STORAGE_BACKEND", default="redis")
STORAGE_HOST=os.environ.get("STORAGE_HOST", default="127.0.0.1")
STORAGE_PORT=os.environ.get("STORAGE_PORT", default=6379)
STORAGE_USER=os.environ.get("STORAGE_USER", default=None)
STORAGE_PASS=os.environ.get("STORAGE_PASS", default=None)

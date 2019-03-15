from werkzeug.exceptions import HTTPException
from flaskapp.core.util import create_api_response


class WebappApiUsageError(Exception):
    code = 400

    def __init__(self, message="Invalid Usage", code=None):
        super(WebappApiUsageError, self).__init__(message)
        self.message = message
        if code is not None and isinstance(code, int):
            self.code = code


def api_exception_handler(err):
    code = 500
    if isinstance(err, HTTPException) or isinstance(err, WebappApiUsageError):
        code = err.code
    return create_api_response(message=err.message, status=code)


def app_exception_handler(err):
    code = err.code if isinstance(err, HTTPException) else 500
    message = (
        f"<h1>Sorry, something went wrong (code: {code})</h1>"
        f"<p>We've logged the error and our team will look at it</p>")

    return message, code

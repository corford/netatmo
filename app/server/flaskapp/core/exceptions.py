class FlaskappNetatmoTokenRefreshError(Exception):
    def __init__(self, message):
        super(FlaskappNetatmoTokenRefreshError, self).__init__(message)
        self.response = {
            'text': message,
            'code': 500
        }


class FlaskappApiError(Exception):
    code = 400

    def __init__(self, message, code=None):
        super(FlaskappApiError, self).__init__(message)
        self.message = message
        if code is not None and isinstance(code, int):
            self.code = code

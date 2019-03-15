from flask import jsonify


def is_int(val):
    try:
        int(val)
    except (TypeError, ValueError):
        return False

    return True


def create_api_response(data=None, status=200, message=''):
    if type(data) is not dict and data is not None:
        raise TypeError('Data should be a dictionary')

    if not is_int(status):
        raise TypeError('Status should be an integer')

    success = True if status >= 200 and status < 300 else False
    response = {'success': success, 'message': message, 'result': data}

    return jsonify(response), status

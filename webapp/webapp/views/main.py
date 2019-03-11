from flask import Blueprint
from flask import current_app as app

bp = Blueprint("main", __name__)  


@bp.route("/", methods=["GET"])
def index():
    return "<h1>Hello World!</h1>"

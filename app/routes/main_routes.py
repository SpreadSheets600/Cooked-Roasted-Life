from . import main_bp
from flask import jsonify


@main_bp.route("/")
def index():
    return jsonify({"message": "Cooked Life Roast API", "status": "running"})

from . import main_bp
from ..models.database import Roast

from flask import render_template, abort


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/roast")
def roast_page():
    return render_template("roast.html")


@main_bp.route("/share/<roast_id>")
def share_roast(roast_id):
    roast = Roast.query.filter_by(id=roast_id).first()

    if not roast:
        abort(404)

    return render_template("share.html", roast=roast)

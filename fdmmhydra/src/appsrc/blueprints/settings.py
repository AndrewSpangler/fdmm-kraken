from flask import Blueprint, render_template

blueprint = Blueprint('settings', __name__)

from ..main import app

@blueprint.route("/settings")
@app.permission_required()
def settings():
    """Settings page - admin only"""
    return render_template("settings.html", links=app.settings_links)
import os
from flask import Flask, Blueprint, url_for, render_template, redirect
from ...main import app

blueprint = Blueprint(
    'admin',
    __name__,
    url_prefix="/",
    static_folder=os.path.join(os.path.dirname(__file__),"static"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)

@blueprint.route("/admin")
@app.permission_required()
def admin():
    """Admin Page"""
    return "Admin"
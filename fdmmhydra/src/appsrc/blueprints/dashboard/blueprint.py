import os
from flask import Flask, Blueprint, url_for, render_template, redirect
from ...main import app

blueprint = Blueprint(
    'dashboard',
    __name__,
    url_prefix="/",
    static_folder=os.path.join(os.path.dirname(__file__),"static"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
)

@blueprint.route("/")
@app.permission_required()
def dashboard():
    return render_template("dashboard.html")
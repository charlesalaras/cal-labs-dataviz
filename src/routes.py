"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return "<a href=\"/dashapp/\">Sign in with Canvas</button>"
"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app
import flask

@app.route('/')
def home():
    """Landing page."""
    return flask.render_template('home.html')

@app.route('/login')
def login():
    canvas = request_oauthlib.OAuth2Session(
        CLIENT_ID, redirect_uri="http://localhost:5000/callback"
    )
    authorization_url, _ = canvas.authorization_url(AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)

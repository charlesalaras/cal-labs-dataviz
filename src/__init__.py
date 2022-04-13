from flask import Flask

def init_app():
   app = Flask(__name__, static_url_path='')

   with app.app_context():
      # Import parts of our core Flask app
      from . import routes

      # Import Dash App
      from .dash.dashboard import init_dashboard
      app = init_dashboard(app)

      # Register Database
      from . import db
      db.init_app(app)

      return app
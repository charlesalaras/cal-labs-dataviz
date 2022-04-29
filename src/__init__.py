from flask import Flask
from flask_pymongo import PyMongo

mongo = None

def init_app():
   app = Flask(__name__, static_url_path='')

   app.config["MONGO_URI"] = "mongodb://localhost:27017/callabs"
   mongo = PyMongo(app)


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

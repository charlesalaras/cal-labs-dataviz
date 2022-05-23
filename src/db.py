import sqlite3
import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DATABASE = os.getenv('DATABASE')
def db_connect():
    client = MongoClient('mongodb://localhost:27017')
    return client

def db_close(client):
    client.close()

def get_db():
   if 'db' not in g:
      g.db = sqlite3.connect(
         DATABASE,
         detect_types=sqlite3.PARSE_DECLTYPES
      )
      g.db.row_factory = sqlite3.Row

   return g.db

def init_db():
   db = get_db()

   with current_app.open_resource('schema.sql') as f:
      db.executescript(f.read().decode('utf8'))

def close_db(e=None):
   db = g.pop('db', None)

   if db is not None:
      db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
   """Clear the existing data and create new tables."""
   init_db()
   click.echo('Initialized the database.')

def init_app(app):
   app.teardown_appcontext(close_db)
   app.cli.add_command(init_db_command)

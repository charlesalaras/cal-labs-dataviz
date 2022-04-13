"""Application entry point."""
from src import init_app
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



app = init_app()




# Naive database setup
'''
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass
'''

if __name__ == "__main__":
    app.run(debug=True)


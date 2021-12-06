"""Application entry point."""
from src import init_app
import os
'''
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

AUTHORIZATION_BASE_URL =
TOKEN_URL =
USERINFO_URL =

# If we can't secure with SSL, we need to turn this on
OS.ENVIRON["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
'''
app = init_app()

if __name__ == "__main__":
    app.run(debug=True)
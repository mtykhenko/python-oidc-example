import datetime
import os

from flask import Flask, Response, jsonify, session
from flask_session import Session

from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

app = Flask(__name__)

#filesystem based session persistence
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Load Flask app and OIDC configuration from prefixed env variables (FLASK_xxxxxxx) provided by deployment
app.config.from_prefixed_env()

CLIENT_METADATA = ClientMetadata(client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
PROVIDER_CONFIG = ProviderConfiguration(issuer=app.config['ISSUER'], client_metadata=CLIENT_METADATA)
PROVIDER_NAME = app.config['PROVIDER_NAME']

auth = OIDCAuthentication({PROVIDER_NAME: PROVIDER_CONFIG}, app=app)

#endpoint that requires authentication and shows access token and user info in case of success
@app.route("/protected")
@auth.oidc_auth(PROVIDER_NAME)
def protected():
    user_session = UserSession(session)
    return jsonify(access_token=user_session.access_token, id_token=user_session.id_token, userinfo=user_session.userinfo)

#public endpoint with unauthorized access
@app.route("/")
def public():
    return Response("This page is publicly open! No auth required")

app.run(host='0.0.0.0', port=5000)
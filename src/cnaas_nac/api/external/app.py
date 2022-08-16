import os
import sys

from cnaas_nac.api.external.auth import api as auth_api
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import Flask, jsonify, logging, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, decode_token
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restx import Api
from jwt.exceptions import (DecodeError, InvalidSignatureError,
                            InvalidTokenError)

logger = get_logger()


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in 'Bearer: <your JWT token here' to autheticate."
    }
}


class CnaasApi(Api):
    def handle_error(self, e):
        if isinstance(e, DecodeError):
            data = {'status': 'error', 'data': 'Could not deode JWT token'}
        elif isinstance(e, InvalidTokenError):
            data = {'status': 'error', 'data': 'Invalid authentication header'}
        elif isinstance(e, InvalidSignatureError):
            data = {'status': 'error', 'data': 'Invalid token signature'}
        elif isinstance(e, IndexError):
            # We might catch IndexErrors which are not cuased by JWT,
            # but this is better than nothing.
            data = {'status': 'error', 'data': 'JWT token missing?'}
        elif isinstance(e, NoAuthorizationError):
            data = {'status': 'error', 'data': 'JWT token missing?'}
        else:
            return super(CnaasApi, self).handle_error(e)

        return jsonify(data)


try:
    # If we don't find a "real" cert, fall back to a self-signed
    # one. We need this for running tests.
    if os.path.exists('/opt/cnaas/certs/jwt_pubkey.pem'):
        cert_path = '/opt/cnaas/certs/jwt_pubkey.pem'
    elif os.path.exists('./src/cert/jwt_pubkey.pem'):
        cert_path = './src/cert/jwt_pubkey.pem'
    else:
        cert_path = './cert/jwt_pubkey.pem'

    logger.debug(f'Reading JWT certificate from {cert_path}')

    jwt_pubkey = open(cert_path).read()
except Exception as e:
    print("Could not load public JWT cert: {0}".format(e))
    sys.exit(1)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(128)
app.config['JWT_PUBLIC_KEY'] = jwt_pubkey
app.config['JWT_IDENTITY_CLAIM'] = 'sub'
app.config['JWT_ALGORITHM'] = 'ES256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)
cors = CORS(app,
            resources={r"/api/*": {"origins": "*"}},
            expose_headers=["Content-Type", "Authorization", "X-Total-Count"])

api = CnaasApi(app, prefix='/api/{}'.format(__api_version__),
               authorizations=authorizations,
               security='apikey')

api.add_namespace(auth_api)


# Log all requests, include username etc
@app.after_request
def log_request(response):
    try:
        token = request.headers.get('Authorization').split(' ')[-1]
        user = decode_token(token).get('sub')
    except Exception:
        user = 'unknown'

    app.logger.info('[External API] User: {}, Method: {}, Status: {}, URL: {}'.format(
        user, request.method, response.status_code, request.url))

    return response

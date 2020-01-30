import os

from flask import Flask, request, jsonify
from flask_restplus import Api
from flask_jwt_extended import JWTManager, decode_token
from flask_jwt_extended.exceptions import NoAuthorizationError

from cnaas_nac.api.auth import api as auth_api
from cnaas_nac.api.webadmin import WebAdmin
from cnaas_nac.version import __api_version__
from cnaas_nac.tools.log import get_logger

from jwt.exceptions import DecodeError, InvalidSignatureError, \
    InvalidTokenError


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


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(128)
app.config['JWT_PUBLIC_KEY'] = open('certs/public.pem').read()
app.config['JWT_IDENTITY_CLAIM'] = 'sub'
app.config['JWT_ALGORITHM'] = 'ES256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)
api = CnaasApi(app, prefix='/api/{}'.format(__api_version__),
               authorizations=authorizations,
               security='apikey')

api.add_namespace(auth_api)

@app.route('/admin', methods=['GET', 'POST'])
def index():
    return WebAdmin.index()


# Log all requests, include username etc
@app.after_request
def log_request(response):
    try:
        token = request.headers.get('Authorization').split(' ')[-1]
        user = decode_token(token).get('sub')
    except Exception:
        user = 'unknown'
    logger.info('User: {}, Method: {}, Status: {}, URL: {}, JSON: {}'.format(
        user, request.method, response.status_code, request.url, request.json))
    return response

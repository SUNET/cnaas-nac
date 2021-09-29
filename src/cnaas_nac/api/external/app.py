import os
import sys
import redis
import random

from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_restx import Api
from flask_jwt_extended import JWTManager, decode_token
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_sse import sse

from cnaas_nac.api.external.auth import api as auth_api
from cnaas_nac.version import __api_version__
from cnaas_nac.tools.log import get_logger

from apscheduler.schedulers.background import BackgroundScheduler

from jwt.exceptions import DecodeError, InvalidSignatureError, \
    InvalidTokenError


logger = get_logger()

try:
    redis_client = redis.Redis(host="nac_redis", port=6379)
    redis_client.ping()
except redis.exceptions.ConnectionError:
    redis_client = redis.Redis(host="localhost", port=6379)
    redis_client.ping()

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


def get_data_accepted():
    data = list()

    try:
        accepted = redis_client.sort(
            "clients", by="*->accepts", start=0, num=10)

        if not accepted:
            return []

        for client in accepted:
            client_accepts = redis_client.hget(client, "accepts")

            if not client_accepts:
                continue

            data.append({client.decode(
                'UTF-8'): client_accepts.decode('UTF-8')})
        data.reverse()
    except Exception as e:
        logger.error(f'Failed to get accepts from Redis: {e}')

    logger.debug(f'[External API] Pushed event for accepted clients: {data}')

    return {'accepted': data}


def get_data_rejected():
    data = list()

    try:
        rejected = redis_client.sort(
            "clients", by="*->rejects", start=0, num=10)

        if not rejected:
            return []

        for client in rejected:
            client_rejects = redis_client.hget(client, "rejects")

            if not client_rejects:
                continue

            data.append({client.decode(
                'UTF-8'): client_rejects.decode('UTF-8')})
        data.reverse()
    except Exception as e:
        logger.error(f'Failed to get rejects from Redis: {e}')

    logger.debug(f'[External API] Pushed event for rejected clients: {data}')

    return {'rejected': data}


def server_event():
    with app.app_context():
        sse.publish(get_data_accepted(), type='accepted_update')
        sse.publish(get_data_rejected(), type='rejected_update')


print(os.path.abspath(os.getcwd()))

try:
    # If we don't find a "real" cert, fall back to a self-signed
    # one. We need this for running tests.
    if os.path.exists('/opt/cnaas/certs/jwt_pubkey.pem'):
        cert_path = '/opt/cnaas/certs/jwt_pubkey.pem'
    elif os.path.exists('./src/cert/jwt_pubkey.pem'):
        cert_path = './src/cert/jwt_pubkey.pem'
    else:
        cert_path = './cert/jwt_pubkey.pem'

    logger.debug(f'[External API] Reading JWT certificate from {cert_path}')

    jwt_pubkey = open(cert_path).read()
except Exception as e:
    logger.debug(
        "[External API] Could not load public JWT cert: {0}".format(e))
    sys.exit(1)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(128)
app.config['JWT_PUBLIC_KEY'] = jwt_pubkey
app.config['JWT_IDENTITY_CLAIM'] = 'sub'
app.config['JWT_ALGORITHM'] = 'ES256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config["REDIS_URL"] = "redis://nac_redis"

jwt = JWTManager(app)
cors = CORS(app,
            resources={r"/api/*": {"origins": "*"}},
            expose_headers=["Content-Type", "Authorization", "X-Total-Count"])

api = CnaasApi(app, prefix='/api/{}'.format(__api_version__),
               authorizations=authorizations,
               security='apikey')

api.add_namespace(auth_api)
app.register_blueprint(sse, url_prefix='/events')


sched = BackgroundScheduler(daemon=True)
sched.add_job(server_event, 'interval', seconds=10)
sched.start()


# Log all requests, include username etc
@app.after_request
def log_request(response):
    try:
        token = request.headers.get('Authorization').split(' ')[-1]
        user = decode_token(token).get('sub')
    except Exception:
        user = 'unknown'
    logger.info('[External API] User: {}, Method: {}, Status: {}, URL: {}, JSON: {}'.format(
        user, request.method, response.status_code, request.url, request.json))
    return response

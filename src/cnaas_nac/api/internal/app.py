import os

from cnaas_nac.api.internal.auth import api as auth_api
from cnaas_nac.tools.log import get_logger
from cnaas_nac.version import __api_version__
from flask import Flask, jsonify, request
from flask_restx import Api
from jwt.exceptions import (DecodeError, InvalidSignatureError,
                            InvalidTokenError)

logger = get_logger()


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
        else:
            return super(CnaasApi, self).handle_error(e)
        return jsonify(data)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(128)

api = CnaasApi(app, prefix='/api/{}'.format(__api_version__))
api.add_namespace(auth_api)

# Log all requests, include username etc


@app.after_request
def log_request(response):
    logger.info('[Internal API] Method: {}, Status: {}, URL: {}'.format(
        request.method, response.status_code, request.url))
    return response

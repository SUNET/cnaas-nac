import os

from flask import Flask, request
from flask_restplus import Api

from cnaas_nac.api.auth import api as auth_api
from cnaas_nac.version import __api_version__
from cnaas_nac.tools.log import get_logger


logger = get_logger()


class CnaasApi(Api):
    def handle_error(self, e):
        return super(CnaasApi, self).handle_error(e)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(128)

api = CnaasApi(app, prefix='/api/{}'.format(__api_version__))
api.add_namespace(auth_api)

# Log all requests, include username etc
@app.after_request
def log_request(response):
    logger.info('Method: {}, Status: {}, URL: {}, JSON: {}'.format(
        request.method, response.status_code, request.url, request.json))
    return response

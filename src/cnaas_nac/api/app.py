from flask import Flask
from flask_restful import Api
from cnaas_nac.api.auth import AuthApi, AuthApiByName
from cnaas_nac.version import __api_version__

import os


API_VERSION = 'v1.0'


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.urandom(128)


api.add_resource(AuthApi, f'/api/{ __api_version__ }/auth')
api.add_resource(AuthApiByName, f'/api/{ __api_version__ }/auth/<string:username>')

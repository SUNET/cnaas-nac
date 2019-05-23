from flask import Flask
from flask_restful import Api
from cnaas_nac.api.auth import AuthApi


API_VERSION = 'v1.0'

app = Flask(__name__)
api = Api(app)


api.add_resource(AuthApi, '/api/v1.0/auth')

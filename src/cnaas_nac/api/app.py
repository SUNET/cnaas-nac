from flask import Flask
from flask_restful import Api
from cnaas_nac.api.auth import AuthApi, AuthApiByName
from cnaas_nac.api.webapi import WebApi

API_VERSION = 'v1.0'

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'kakakekekeff'

@app.route('/', methods=['GET', 'POST'])
def index():
    return WebApi.index()
    
api.add_resource(AuthApi, '/api/v1.0/auth')
api.add_resource(AuthApiByName, '/api/v1.0/auth/<string:username>')

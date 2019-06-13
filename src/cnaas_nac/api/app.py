from flask import Flask
from flask_restful import Api
from cnaas_nac.api.auth import AuthApi, AuthApiByName
from cnaas_nac.api.webapi import WebApi

from cnaas_nac.version import __api_version__


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'kakakekekeff'

@app.route('/', methods=['GET', 'POST'])
def index():
    return WebApi.index()


api.add_resource(AuthApi, f'/api/{ __api_version__ }/auth')
api.add_resource(AuthApiByName, f'/api/{ __api_version__ }/auth/<string:username>')

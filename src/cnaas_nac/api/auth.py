from flask import request
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User
from cnaas_nac.version import __api_version__


logger = get_logger()


api = Namespace('auth', description='Authentication API',
                     prefix='/api/{}'.format(__api_version__))

user_add = api.model('auth', {
    'EAP-Message': fields.String(required=False),
    'username': fields.String(required=False),
    'password': fields.String(required=False),
    'vlan': fields.Integer(required=False)
})

user_enable = api.model('auth_enable', {
    'enable': fields.Boolean(required=True)
})


class AuthApi(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    @jwt_required
    def get(self):
        user = User.user_get()
        for _ in user:
            reply = User.reply_get(_['username'])
            _['reply'] = reply
        reply = User.reply_get('test0')
        result = {'users': user}
        return empty_result(status='success', data=result)

    @jwt_required
    @api.expect(user_add)
    def post(self):
        errors = []
        json_data = request.get_json()

        # We should only handle clients using MAB. If the user authenticates
        # with 802.1X we will get an EAP message, just return a 202 and don't
        # create that user in the database.
        if 'EAP-Message' in json_data:
            logger.info('EAP-message, ignoring')
            return empty_result(status='success')

        users = User.user_get(json_data['username'])
        for _ in users:
            if _ == json_data['username']:
                logger.info('User {} already exists'.format(_))
                return empty_result(status='success')

        if 'username' not in json_data:
            return self.error('Username not found')
        if 'password' not in json_data:
            json_data['password'] = json_data['username']
        if 'vlan' in json_data:
            try:
                vlan = int(json_data['vlan'])
            except Exception:
                return self.error('Invalid VLAN')
        else:
            json_data['vlan'] = 100
        result = User.user_add(json_data['username'], json_data['password'])
        if result != '':
            errors.append(result)
        if json_data['vlan'] != 0:
            result = User.reply_add(json_data['username'], json_data['vlan'])
        if result != '':
            errors.append(result)
        if errors != []:
            logger.info('Error: {}'.format(errors))
            return self.error(errors)
        user = User.user_get(json_data['username'])
        logger.info('User: {}'.format(user))
        return empty_result(status='success', data=user)


class AuthApiByName(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    @jwt_required
    def get(self, username):
        user = User.user_get(username)
        for _ in user:
            reply = User.reply_get(_['username'])
            _['reply'] = reply
        result = {'users': user}
        return empty_result(status='success', data=result)

    @jwt_required
    @api.expect(user_enable)
    def put(self, username):
        json_data = request.get_json()
        result = ''
        if 'enabled' not in json_data:
            return self.error('Missing argument enabled in JSON string')
        if json_data['enabled'] is True:
            result = User.user_enable(username)
        else:
            result = User.user_disable(username)
        if result != '':
            return self.error(result)
        return empty_result(status='success')

    @jwt_required
    def delete(self, username):
        errors = []
        result = User.user_del(username)
        if result != '':
            errors.append(result)
        result = User.reply_del(username)
        if result != '':
            errors.append(result)
        if errors != []:
            return self.error(errors)
        return empty_result(status='success')


api.add_resource(AuthApi, '')
api.add_resource(AuthApiByName, '/<string:username>')

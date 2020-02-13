from flask import request
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, PostAuth
from cnaas_nac.db.oui import DeviceOui
from cnaas_nac.db.nas import NasPort
from cnaas_nac.tools.helpers import get_user_replies, get_user_port, \
    get_is_active, get_last_seen

from cnaas_nac.version import __api_version__


logger = get_logger()


api = Namespace('auth', description='Authentication API',
                prefix='/api/{}'.format(__api_version__))

user_add = api.model('auth', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'vlan': fields.Integer(required=True),
    'nas_identifier': fields.String(required=True),
    'nas_port_id': fields.String(required=True),
    'calling_station_id': fields.String(required=True),
    'called_station_id': fields.String(required=True)
})

user_enable = api.model('auth_enable', {
    'enable': fields.Boolean(required=True)
})


def get_user_data(username=''):
    result = dict()

    users = User.get(username)
    replies = User.reply_get()
    nas_ports = NasPort.get()
    last_seen = PostAuth.get_last_seen()

    for user in users:
        username = user['username']
        result[username] = dict()
        nas_port = get_user_port(username, nas_ports)

        if nas_port is None:
            nas_port = dict()
            nas_port['nas_identifier'] = None
            nas_port['nas_port_id'] = None
            nas_port['called_station_id'] = None
            nas_port['calling_station_id'] = None

        for key in nas_port:
            result[username][key] = nas_port[key]

        result[username]['active'] = get_is_active(username, users)
        result[username]['last_seen'] = get_last_seen(username, last_seen)
        result[username]['replies'] = get_user_replies(username, replies)
    return result


class AuthApi(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    @jwt_required
    def get(self):
        return empty_result(status='success', data=get_user_data())

    @api.expect(user_add)
    def post(self):
        errors = []
        json_data = request.get_json()

        # We should only handle clients using MAB. If the user authenticates
        # with 802.1X we will get an EAP message, just return a 202 and don't
        # create that user in the database.
        if 'eap_message' in json_data and json_data['eap_message'] != '':
            logger.info('EAP-message, ignoring')
            return empty_result(status='success')

        if 'username' not in json_data:
            return self.error('Username not found')

        username = json_data['username']

        if 'nas_identifier' not in json_data:
            nas_identifier = None
        else:
            nas_identifier = json_data['nas_identifier']

        if 'nas_port_id' not in json_data:
            nas_port_id = None
        else:
            nas_port_id = json_data['nas_port_id']

        if 'calling_station_id' not in json_data:
            calling_station_id = None
        else:
            calling_station_id = json_data['calling_station_id']

        if 'called_station_id' not in json_data:
            called_station_id = None
        else:
            called_station_id = json_data['called_station_id']

        if nas_identifier == "" or nas_identifier is None:
            nas_identifier = username

        for user in User.get(username):
            if user == username:
                logger.info('User {} already exists'.format(user))
                nas_port = NasPort.get(username)
                if nas_port['nas_identifier'] != nas_identifier:
                    return self.error('User already exist on {}'.format(
                        nas_port['nas_identifier']))
                if nas_port['nas_port'] != nas_port:
                    return self.error('User already exist on port {}'.format(
                        nas_port['nas_port']))
                return empty_result(status='success')

        if 'password' not in json_data:
            password = username
        else:
            password = json_data['password']

        if 'vlan' in json_data:
            try:
                vlan = int(json_data['vlan'])
            except Exception:
                return self.error('Invalid VLAN')
        else:
            vlan = 13

        if User.add(username, password) != '':
            logger.info('Not creating user {} again'.format(username))

        if User.reply_add(username, vlan) != '':
            logger.info('Not creating reply for user {}'.format(username))
        else:
            if DeviceOui.exists(username):
                logger.info('Setting user VLAN to OUI VLAN.')
                oui_vlan = DeviceOui.get_vlan(username)
                User.enable(username)
                User.reply_vlan(username, oui_vlan)

        if NasPort.add(username, nas_identifier, nas_port_id,
                       calling_station_id,
                       called_station_id) != '':
            logger.info('Not adding NAS port again.')

        if errors != []:
            logger.info('Error: {}'.format(errors))
            return self.error(errors)

        user = User.get(username)
        logger.info('User: {}'.format(user))

        return empty_result(status='success', data=user)


class AuthApiByName(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    @jwt_required
    def get(self, username):
        return empty_result(status='success', data=get_user_data(username))

    @jwt_required
    @api.expect(user_enable)
    def put(self, username):
        json_data = request.get_json()
        result = ''

        if 'enabled' in json_data:
            if json_data['enabled'] is True:
                result = User.enable(username)
            else:
                result = User.disable(username)
        if 'vlan' in json_data:
            print('Setting VLAN')
            result = User.reply_vlan(username, json_data['vlan'])
        if result != '':
            return self.error(result)
        return empty_result(status='success')

    @jwt_required
    def delete(self, username):
        errors = []
        result = User.delete(username)
        if result != '':
            errors.append(result)
        result = User.reply_delete(username)
        if result != '':
            errors.append(result)
        if errors != []:
            return self.error(errors)
        return empty_result(status='success')


api.add_resource(AuthApi, '')
api.add_resource(AuthApiByName, '/<string:username>')

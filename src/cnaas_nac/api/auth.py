import os

from flask import request
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, get_users, UserInfo
from cnaas_nac.db.oui import DeviceOui
from cnaas_nac.db.nas import NasPort

from cnaas_nac.version import __api_version__


logger = get_logger()


api = Namespace('auth', description='Authentication API',
                prefix='/api/{}'.format(__api_version__))

user_add = api.model('auth', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'vlan': fields.Integer(required=True),
    'nas_identifier': fields.String(required=True),
    'nas_ip_address': fields.String(required=True),
    'nas_port_id': fields.String(required=True),
    'calling_station_id': fields.String(required=True),
    'called_station_id': fields.String(required=True),
    'eap': fields.String(required=False)
})

user_enable = api.model('auth_enable', {
    'enable': fields.Boolean(required=True)
})


def accept(username, data={}):
    UserInfo.add(username, reason='')

    json_reply = dict()
    replies = User.reply_get()

    for reply in replies:
        json_reply[reply['attribute']] = {
            'op': reply['op'],
            'value': reply['value']
        }

    return json_reply


def reject(username, errstr=''):
    UserInfo.add(username, reason=errstr)
    return empty_result(status='error', data=errstr), 404


class AuthApi(Resource):
    def validate(self, json_data):
        if 'username' not in json_data:
            raise ValueError('Username not found')
        else:
            username = json_data['username']

        if 'password' in json_data:
            password = json_data['password']
        else:
            password = username

        if 'vlan' in json_data:
            vlan = json_data['vlan']
        else:
            vlan = 13

        if 'nas_identifier' not in json_data:
            nas_identifier = None
        else:
            nas_identifier = json_data['nas_identifier']

        if 'nas_port_id' not in json_data:
            nas_port_id = None
        else:
            nas_port_id = json_data['nas_port_id']

        if 'nas_ip_address' not in json_data:
            nas_ip_address = None
        else:
            nas_ip_address = json_data['nas_ip_address']

        if 'calling_station_id' not in json_data:
            calling_station_id = None
        else:
            calling_station_id = json_data['calling_station_id']

        if 'called_station_id' not in json_data:
            called_station_id = None
        else:
            called_station_id = json_data['called_station_id']

        if 'eap' not in json_data:
            eap = None
        else:
            eap = json_data['eap']

        if nas_identifier == "" or nas_identifier is None:
            nas_identifier = username

        return username, password, vlan, nas_identifier, nas_port_id, \
            calling_station_id, called_station_id, nas_identifier, \
            nas_ip_address, eap

    # @jwt_required
    def get(self):
        return empty_result(status='success', data=get_users())

    @api.expect(user_add)
    def post(self):
        errors = []
        json_data = request.get_json()

        try:
            (username, password, vlan, nas_identifier, nas_port_id,
             calling_station_id, called_station_id, nas_identifier,
             nas_ip_address, eap) = self.validate(json_data)
        except Exception as e:
            return reject(username, str(e))

        for user in User.get(username):
            # Find the current user.
            if user['username'] != username:
                continue

            logger.info('User {} exists.'.format(user['username']))

            # Find out all configured ports for the current user.
            nas_ports = NasPort.get(username)

            if nas_ports is not None and eap is None or eap == '':
                for port in nas_ports:
                    if port['nas_port_id'] == nas_port_id and port['called_station_id'] == called_station_id:
                        logger.info('Valid NAS port {} on {} for user {}.'.format(
                            nas_port_id, called_station_id, username))

                        # Only accept the user it is enabled.
                        if User.is_enabled(username):
                            logger.info('Valid NAS port and active, accepting.')
                            return accept(username)
                    else:
                        logger.info('{} on {}, expected {} on {}.'.format(
                            nas_port_id,
                            called_station_id,
                            port['nas_port_id'],
                            port['called_station_id']))

                        return reject(username,
                                      '{}/{}, expected {}/{}'.format(
                                          called_station_id, nas_port_id,
                                          port['called_station_id'],
                                          port['nas_port_id']))

        if 'RADIUS_SLAVE' in os.environ:
            if os.environ['RADIUS_SLAVE'] == 'yes':
                if User.is_enabled(username):
                    return accept(username)
                else:
                    logger.info('Slave mode, user disabled. Rejecting.')
                    return reject(username, 'User disabled')

        if eap is not None and eap != '':
            if User.is_enabled(username):
                return accept(username)
            else:
                return reject(username)

        if User.add(username, password) != '':
            logger.info('Not creating user {} again.'.format(username))

        if User.reply_add(username, vlan) != '':
            logger.info('Not creating reply for user {}.'.format(username))
        else:
            if DeviceOui.exists(username):
                logger.info('Setting user VLAN to OUI VLAN.')

                oui_vlan = DeviceOui.get_vlan(username)

                User.reply_vlan(username, oui_vlan)
                User.enable(username)

        res = NasPort.add(username, nas_ip_address, nas_identifier,
                          nas_port_id,
                          calling_station_id,
                          called_station_id)
        if res != '':
            logger.info(res)

        if User.is_enabled(username):
            return accept(username)

        if errors != []:
            logger.info('Error: {}'.format(errors))
            return reject(username, errors)

        logger.info('User did not match any rules, rejeecting.')
        return reject(username, 'User disabled.')


class AuthApiByName(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    # @jwt_required
    def get(self, username):
        return empty_result(status='success', data=get_users(username))

    # @jwt_required
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
            result = User.reply_vlan(username, json_data['vlan'])
        if result != '':
            return empty_result(status='error', data=result), 404
        return empty_result(status='success')

    # @jwt_required
    def delete(self, username):
        errors = []
        result = User.delete(username)
        if result != '':
            return empty_result(status='error', data=result), 404

        result = User.reply_delete(username)
        if result != '':
            errors.append(result)

        result = NasPort.delete(username)
        if result != '':
            errors.append(result)

        result = UserInfo.delete(username)
        if result != '':
            errors.append(result)

        if errors != []:
            return reject(errors)
        return empty_result(status='success')


api.add_resource(AuthApi, '')
api.add_resource(AuthApiByName, '/<string:username>')

import os

from flask import request
from flask_restplus import Resource, Namespace, fields

from cnaas_nac.api.internal.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, get_users, UserInfo
from cnaas_nac.db.oui import DeviceOui
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.reply import Reply

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
    'called_station_id': fields.String(required=True)
})

user_edit = api.model('auth_enable', {
    'enable': fields.Boolean(required=False),
    'vlan': fields.String(required=False)
})


def accept(username):
    """
    Send the user an Access-Accept and include the different replies
    in the response. According to FreeRADIUS documentation the response
    should return JSON data with the attributes in the following format:

    {
        "Tunnel-Type": {
            "op": "=",
            "value": "VLAN"
        },
        "Tunnel-Medium-Type": {
            "op": "=",
            "value": "IEEE-802"
        },
        "Tunnel-Private-Group-Id": {
            "op": "=",
            "value": "13"
        }
    }
    """
    json_reply = {}

    for reply in Reply.get(username):
        json_reply[reply['attribute']] = {
            'op': reply['op'],
            'value': reply['value']
        }

    UserInfo.add(username, reason='User accepted', auth=True)

    return json_reply


def reject(username, errstr=''):
    """
    Reject the user with a 404.
    """
    UserInfo.add(username, reason=errstr, auth=True)
    return empty_result(status='error', data=errstr), 404


class AuthApi(Resource):
    def validate(self, json_data):
        """
        Validate all the JSON attributes we get from FreeRADIUS.
        We expect to get the following:

        * username
        * password
        * vlan
        * nas_identifier
        * nas_port_id
        * nas_ip_address
        * calling_station_id
        * called_station_id
        """

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

        if nas_identifier == "" or nas_identifier is None:
            nas_identifier = username

        return username, password, vlan, nas_identifier, nas_port_id, \
            calling_station_id, called_station_id, nas_identifier, \
            nas_ip_address

    def get(self):
        """
        Get a JSON blob with all users, replies and other information.
        """

        return empty_result(status='success', data=get_users())

    def check_nas_port(self, username, nas_port, called_station_id,
                       nas_port_id):
        """ Check the current NAS port and called station for the user. If
        this differ from what is configured we should reject the
        user. That meanswe should block users that are moved from one
        switch port to another.
        """

        if nas_port is None:
            return ''

        if nas_port['nas_port_id'] != nas_port_id:
            return 'On {}, expected {}'.format(
                nas_port_id,
                nas_port['nas_port_id'])

        if nas_port['called_station_id'] != called_station_id:
            return 'On {}, expected {}'.format(
                called_station_id,
                nas_port['called_station_id'])

        if User.is_enabled(username):
            return ''

        return ''

    @api.expect(user_add)
    def post(self):
        """
        If the user exists, check if it is enabled and if it should be
        accepted or not. If the user don't exist we should create it
        together with attributes and some other information.
        """

        errors = []
        json_data = request.get_json()

        try:
            (username, password, vlan, nas_identifier, nas_port_id,
             calling_station_id, called_station_id, nas_identifier,
             nas_ip_address) = self.validate(json_data)
        except Exception as e:
            return reject('None', str(e))

        for user in User.get(username):
            if user['username'] != username:
                continue

            logger.info('[{}] User already exists.'.format(user['username']))

            nas_ports = NasPort.get(username)

            if not User.is_enabled(username):
                logger.info('[{}] User is disabled'.format(username))
                if nas_ports['nas_port_id'] != nas_port_id or \
                   nas_ports['called_station_id'] != called_station_id:

                    logger.info('[{}] Updating port info'.format(username))
                    NasPort.delete(username)
                    NasPort.add(username, nas_ip_address, nas_identifier,
                                nas_port_id,
                                calling_station_id,
                                called_station_id)
                    nas_ports['nas_port_id'] = nas_port_id
                    nas_ports['called_station_id'] = called_station_id

            res = self.check_nas_port(username, nas_ports,
                                      called_station_id,
                                      nas_port_id)

            if res != '':
                logger.info('[{}] {}'.format(username, res))
                return reject(username, errstr=res)

        # If we are running in slave mode we don't want to create
        # any new users. Check existing users and accept if they exist
        # and are enabled.
        if 'RADIUS_SLAVE' in os.environ:
            if os.environ['RADIUS_SLAVE'] == 'yes':
                if User.is_enabled(username):
                    return accept(username)
                else:
                    logger.info('[{}] Slave mode, user disabled. Rejecting.'.format(username))
                    return reject(username, 'User is disabled')

        # If we don't run in slave mode and the user don't exist,
        # create it and set the default reply (VLAN 13).
        if User.add(username, password) != '':
            logger.info('[{}] Not creating user again'.format(username))

        if Reply.add(username, vlan) != '':
            logger.info('[{}] Not creating reply for user'.format(username))
        else:
            if DeviceOui.exists(username):
                logger.info('[{}] Setting user VLAN to OUI VLAN.'.format(
                    username))

                oui_vlan = DeviceOui.get_vlan(username)

                Reply.vlan(username, oui_vlan)
                User.enable(username)

        res = NasPort.add(username, nas_ip_address, nas_identifier,
                          nas_port_id,
                          calling_station_id,
                          called_station_id)
        if res != '':
            logger.info('[{}] {}'.format(username, res))

        if User.is_enabled(username):
            return accept(username)

        if errors != []:
            logger.info('[{}] Error: {}'.format(username, errors))
            return reject(username, errors)

        logger.info('[{}] User did not match any rules, rejeecting'.format(
            username))
        return reject(username, 'User is disabled')


class AuthApiByName(Resource):
    def get(self, username):
        """
        Return a JSON blob with all users, VLANs and other information.
        """
        return empty_result(status='success', data=get_users(username))

    @api.expect(user_edit)
    def put(self, username):
        """
        Update user parameters such as VLAN, if the user is
        enabled/disabled and so on.
        """
        json_data = request.get_json()
        result = ''

        if 'enabled' in json_data:
            if json_data['enabled'] is True:
                result = User.enable(username)
            else:
                result = User.disable(username)
            UserInfo.add(username, reason='', auth=True)
        if 'vlan' in json_data:
            result = Reply.vlan(username, json_data['vlan'])
        if 'comment' in json_data:
            result = UserInfo.add(username, comment=json_data['comment'])
        if result != '':
            return empty_result(status='error', data=result), 404
        return empty_result(status='success')

    def delete(self, username):
        """
        Remove a user.
        """
        errors = []
        result = User.delete(username)
        if result != '':
            errors.append(result)

        result = Reply.delete(username)
        if result != '':
            errors.append(result)

        result = NasPort.delete(username)
        if result != '':
            errors.append(result)

        result = UserInfo.delete(username)
        if result != '':
            errors.append(result)

        if errors != []:
            return reject(username, errors)
        return empty_result(status='success')


api.add_resource(AuthApi, '')
api.add_resource(AuthApiByName, '/<string:username>')

import os
import json

from flask import request, make_response
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, get_users, UserInfo
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.reply import Reply
from cnaas_nac.api.external.coa import CoA
from cnaas_nac.version import __api_version__

from netaddr import EUI, mac_unix_expanded

logger = get_logger()


api = Namespace('auth', description='Authentication API',
                prefix='/api/{}'.format(__api_version__))

user_edit = api.model('auth_enable', {
    'enable': fields.Boolean(required=False),
    'vlan': fields.String(required=False),
    'comment': fields.String(required=False),
    'bounce': fields.String(required=False)
})


class AuthApi(Resource):
    @jwt_required
    def get(self):
        """
        Get a JSON blob with all users, replies and other information.
        """
        field = None
        condition = ''
        direction = 'username'

        for arg in request.args:
            if 'filter' in arg:
                field = arg[arg.find('[')+1: arg.find(']')]
                condition = request.args[arg].split('?')[0]
            if 'sort' in arg:
                direction = request.args[arg]

        users = get_users(field=field, condition=condition, order=direction)
        response = make_response(json.dumps(empty_result(status='success',
                                                         data=users)), 200)

        response.headers['X-Total-Count'] = len(users)
        response.headers['Content-Type'] = 'application/json'

        return response

    @jwt_required
    def post(self):
        """
        Add a user manually.
        """

        if 'RADIUS_SLAVE' in os.environ:
            if os.environ['RADIUS_SLAVE'] == 'yes':
                return empty_result(status='error',
                                    data='Users can only be added to master server.'), 400

        json_data = request.get_json()

        if 'username' not in json_data:
            return empty_result(status='error',
                                data='username is a required argument'), 400

        try:
            username = str(EUI(
                json_data['username'], dialect=mac_unix_expanded))
        except Exception:
            username = json_data['username']

        if 'password' in json_data:
            try:
                password = str(EUI(
                    json_data['password'], dialect=mac_unix_expanded))
            except Exception:
                password = json_data['password']
        else:
            password = username

        if 'vlan' in json_data:
            vlan = json_data['vlan']
        else:
            if 'RADIUS_DEFAULT_VLAN' in os.environ:
                vlan = os.environ['RADIUS_DEFAULT_VLAN']
            else:
                vlan = 13

        if 'comment' in json_data:
            comment = json_data['comment']
        else:
            comment = None

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

        err = User.add(username, password)

        if err != "":
            return empty_result(status="error", data=err), 400

        err = Reply.add(username, vlan)

        if err != "":
            return empty_result(status="error", data=err), 400

        err = UserInfo.add(username, comment)

        if err != "":
            return empty_result(status="error", data=err), 400

        err = NasPort.add(username, nas_ip_address, nas_identifier, nas_port_id,
                          calling_station_id,
                          called_station_id)

        if err != "":
            return empty_result(status="error", data=err), 400

        if 'active' in json_data and isinstance(json_data['active'], bool):
            if json_data['active']:
                User.enable(username)

        user = get_users(field='username', condition=username)
        response = make_response(json.dumps(empty_result(status='success',
                                                         data=user)), 200)
        return response


class AuthApiByName(Resource):
    @jwt_required
    def get(self, username):
        """
        Return a JSON blob with all users, VLANs and other information.
        """
        users = get_users(field='username', condition=username)
        response = make_response(json.dumps(empty_result(status='success',
                                                         data=users)), 200)

        response.headers['X-Total-Count'] = len(users)
        response.headers['Content-Type'] = 'application/json'

        return response

    @api.expect(user_edit)
    @jwt_required
    def put(self, username):
        """
        Update user parameters such as VLAN, if the user is
        enabled/disabled and so on.
        """
        json_data = request.get_json()
        result = ''

        if json_data is None:
            return empty_result(status='error', data='No JSON input found'), 400

        if 'active' in json_data:
            if json_data['active'] is True:
                result = User.enable(username)
            else:
                result = User.disable(username)
            UserInfo.add(username, reason='', auth=True)
        if 'vlan' in json_data:
            result = Reply.vlan(username, json_data['vlan'])
        if 'comment' in json_data:
            result = UserInfo.add(username, comment=json_data['comment'])
        if 'bounce' in json_data and json_data['bounce'] is True:
            userdata = get_users(field='username', condition=username)
            if userdata == []:
                return empty_result(status='error', data='User not found')

            nas_ip_address = userdata[0]['nas_ip_address']
            nas_port_id = userdata[0]['nas_port_id']

            attrs = {
                'NAS-IP-Address': nas_ip_address,
                'NAS-Port-Id': nas_port_id,
                'Arista-PortFlap': '1'
            }

            if 'RADIUS_COA_SECRET' not in os.environ:
                return empty_result(status='error', data='CoA secret not configured.'), 400
            secret = str.encode(os.environ['RADIUS_COA_SECRET'])

            try:
                coa_request = CoA(nas_ip_address, secret)
                coa_request.send_packet(attrs=attrs)
            except Exception as e:
                result = str(e)

        if result != '':
            return empty_result(status='error', data=result), 400

        return empty_result(status='success',
                            data=get_users(field='username', condition=username))

    @jwt_required
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
            return empty_result(status='error', data=errors), 400
        return empty_result(status='success', data=[])


api.add_resource(AuthApi, '')
api.add_resource(AuthApi, '/')
api.add_resource(AuthApiByName, '/<string:username>')
api.add_resource(AuthApiByName, '/<string:username>/')

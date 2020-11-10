import os
import json

from flask import request, make_response
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, get_users, UserInfo
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.reply import Reply
from cnaas_nac.api.external.coa import CoA
from cnaas_nac.version import __api_version__


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
                condition = request.args[arg]
            if 'sort' in arg:
                direction = request.args[arg]

        users = get_users(field=field, condition=condition, order=direction)
        response = make_response(json.dumps(empty_result(status='success',
                                                         data=users)), 200)

        response.headers['X-Total-Count'] = len(users)
        response.headers['Content-Type'] = 'application/json'

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
        if 'bounce' in json_data and json_data['bounce'] is True:
            userdata = get_users(field='username', condition=username)
            if userdata is []:
                return empty_result(status='error', data='User not found')

            nas_ip_address = userdata[0]['nas_ip_address']
            nas_port_id = userdata[0]['nas_port_id']

            attrs = {
                'NAS-IP-Address': nas_ip_address,
                'NAS-Port-Id': nas_port_id,
                'Arista-PortFlap': '1'
            }

            secret = str.encode(os.environ('RADIUS_COA_SECRET'))

            try:
                coa_request = CoA(nas_ip_address, secret)
                coa_request.send_packet(attrs=attrs)
            except Exception as e:
                result = str(e)

        if result != '':
            return empty_result(status='error', data=result), 400

        return empty_result(status='success')

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
        return empty_result(status='success')


api.add_resource(AuthApi, '')
api.add_resource(AuthApi, '/')
api.add_resource(AuthApiByName, '/<string:username>')
api.add_resource(AuthApiByName, '/<string:username>/')

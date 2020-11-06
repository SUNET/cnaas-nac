from flask import request
from flask_restplus import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from cnaas_nac.api.generic import empty_result
from cnaas_nac.tools.log import get_logger
from cnaas_nac.db.user import User, get_users, UserInfo
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.reply import Reply

from cnaas_nac.version import __api_version__


logger = get_logger()


api = Namespace('auth', description='Authentication API',
                prefix='/api/{}'.format(__api_version__))

user_edit = api.model('auth_enable', {
    'enable': fields.Boolean(required=False),
    'vlan': fields.String(required=False),
    'comment': fields.String(required=False)
})


class AuthApiByName(Resource):
    @jwt_required
    def get(self, username):
        """
        Return a JSON blob with all users, VLANs and other information.
        """
        return empty_result(status='success', data=get_users(username))

    @api.expect(user_edit)
    @jwt_required
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


api.add_resource(AuthApiByName, '/<string:username>')

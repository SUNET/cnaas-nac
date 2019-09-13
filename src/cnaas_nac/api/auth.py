from cnaas_nac.api.generic import empty_result
from cnaas_nac.db.user import User

from flask import request
from flask_restful import Resource


class AuthApi(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    def get(self):
        user = User.user_get()
        for _ in user:
            reply = User.reply_get(_['username'])
            _['reply'] = reply
        reply = User.reply_get('test0')
        result = {'users': user}
        return empty_result(status='success', data=result)

    def post(self):
        errors = []
        json_data = request.get_json()

        # We should only handle clients using MAB. If the user authenticates
        # with 802.1X we will get an EAP message, just return a 202 and don't
        # create that user in the database.
        if 'EAP-Message' in json_data:
            return empty_result(status='success')

        users = User.user_get(json_data['username'])
        for _ in users:
            if _ == json_data['username']:
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
            return self.error(errors)
        return empty_result(status='success')


class AuthApiByName(Resource):
    def error(self, errstr):
        return empty_result(status='error', data=errstr), 404

    def get(self, username):
        user = User.user_get(username)
        for _ in user:
            reply = User.reply_get(_['username'])
            _['reply'] = reply
        result = {'users': user}
        return empty_result(status='success', data=result)

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

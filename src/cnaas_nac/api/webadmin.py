#
# Fugly UI, should at some point be replaced with a proper UI written
# in React and some other facy JS techniques.
#
#

import os
import requests

from flask import request
from flask import redirect
from flask import render_template
from flask_restful import Resource

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    vlan = StringField('VLAN',  validators=[DataRequired()])
    selected = BooleanField('selectfield', default=False)
    submit = SubmitField('Add user')
    delete = SubmitField('Delete user(s)')
    enable = SubmitField('Enable user(s)')
    disable = SubmitField('Disable user(s)')
    set_vlan_btn = SubmitField('Set VLAN')
    set_vlan = StringField()


def get_users(api_url, token):
    try:
        res = requests.get(api_url,
                           headers={'Authorization': 'Bearer ' + token},
                           verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def add_user(api_url, token, username, password, vlan):
    try:
        user = {
            'username': username,
            'password': password,
            'vlan': vlan
        }

        res = requests.post(api_url, json=user,
                            headers={'Authorization': 'Bearer ' + token},
                            verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def delete_user(api_url, token, username):
    try:
        res = requests.delete('{}/{}'.format(api_url, username),
                              headers={'Authorization': 'Bearer ' + token},
                              verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def enable_user(api_url, token, username):
    try:
        user = {'enabled': True}
        res = requests.put('{}/{}'.format(api_url, username), json=user,
                           headers={'Authorization': 'Bearer ' + token},
                           verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def disable_user(api_url, token, username):
    try:
        user = {'enabled': False}
        res = requests.put('{}/{}'.format(api_url, username), json=user,
                           headers={'Authorization': 'Bearer ' + token},
                           verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def vlan_user(api_url, token, username, vlan):
    try:
        user = {'vlan': vlan}
        res = requests.put('{}/{}'.format(api_url, username), json=user,
                           headers={'Authorization': 'Bearer ' + token},
                           verify=False)
        json = res.json()
    except Exception as e:
        print(str(e))
        return {}

    if 'data' in json:
        return json['data']
    return {}


def get_jwt_token():
    try:
        token = os.environ['JWT_AUTH_TOKEN']
    except Exception:
        raise ValueError('Could not find JWT token')
    return token


def get_api_url():
    try:
        token = os.environ['AUTH_API_URL']
    except Exception:
        raise ValueError('Could not find API URL')
    return token


class WebAdmin(Resource):
    @classmethod
    def index(cls):
        api_url = get_api_url()
        token = get_jwt_token()
        users = get_users(api_url, token)
        form = UserForm()

        if request.method == 'POST':
            result = request.form

            if 'submit' in result:
                username = result['username']
                password = result['password']
                vlan = result['vlan']

                add_user(api_url, token, username, password, vlan)
            elif 'delete' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    delete_user(api_url, token, user)
            elif 'enable' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    enable_user(api_url, token, user)
            elif 'disable' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    disable_user(api_url, token, user)
            elif 'set_vlan_btn' in result:
                set_vlan = result['set_vlan']
                if set_vlan != "" and set_vlan:
                    selected = request.form.getlist('selected')
                    for user in selected:
                        vlan_user(api_url, token, user, set_vlan)
            return redirect('/admin')

        return render_template('index.html', users=users,
                               form=form)

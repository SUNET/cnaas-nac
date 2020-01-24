from flask import request
from flask import redirect
from flask import render_template

from flask_restful import Resource

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from cnaas_nac.db.user import User, PostAuth
from cnaas_nac.db.nas import NasPort
from cnaas_nac.db.oui import DeviceOui


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


class WebAdmin(Resource):
    @classmethod
    def index(cls):
        users = User.get()
        form = UserForm()
        ouis = DeviceOui.get()

        for user in users:
            reply = User.reply_get(user['username'])
            nas_port = NasPort.get(user['username'])

            if nas_port is None:
                nas_port = dict()
                nas_port['nas_identifier'] = None
                nas_port['nas_port_id'] = None

            user['reply'] = reply

            if nas_port is not None:
                if 'calling_station_id' in nas_port:
                    user['calling_station_id'] = nas_port['calling_station_id']
                if 'calling_station_id' in nas_port:
                    user['called_station_id'] = nas_port['called_station_id']
                if 'nas_identifier' in nas_port:
                    user['nas_identifier'] = nas_port['nas_identifier']
                if 'nas_port_id' in nas_port:
                    user['nas_port_id'] = nas_port['nas_port_id']
                user['active'] = User.is_enabled(user['username'])
            user['active'] = User.is_enabled(user['username'])
            user['last_seen'] = PostAuth.get_last_seen(user['username'])

        if request.method == 'POST':
            result = request.form

            if 'submit' in result:
                username = result['username']
                password = result['password']
                vlan = result['vlan']

                User.add(username, password)
                User.reply_add(username, vlan)
                User.disable(username)
            elif 'delete' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    User.delete(user)
                    User.reply_delete(user)
            elif 'enable' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    User.enable(user)
            elif 'disable' in result:
                selected = request.form.getlist('selected')
                for user in selected:
                    User.disable(user)
            elif 'set_vlan_btn' in result:
                set_vlan = result['set_vlan']
                if set_vlan != "" and set_vlan:
                    selected = request.form.getlist('selected')
                    for user in selected:
                        User.reply_vlan(user, set_vlan)
            return redirect('/admin')

        return render_template('index.html', users=users, ouis=ouis, form=form)

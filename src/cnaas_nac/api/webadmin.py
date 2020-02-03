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
    def get_user_reply(cls, username, replies):
        reply = []
        for user_reply in replies:
            if user_reply['username'] == username:
                reply.append(user_reply)
        return reply

    @classmethod
    def user_get_port(cls, username, nas_ports):
        nas_port = None
        for port in nas_ports:
            if port['username'] == username:
                nas_port = port
        return nas_port

    @classmethod
    def user_is_active(cls, username, users):
        for user in users:
            if 'username' not in user:
                continue
            if user['username'] != username:
                continue
            if user['op'] == ':=':
                return True
        return False

    @classmethod
    def user_last_seen(cls, username, last_seen):
        for user in last_seen:
            if 'username' not in user:
                continue
            if user['username'] != username:
                continue
            return user['authdate']
        return None

    @classmethod
    def index(cls):
        users = User.get()
        form = UserForm()
        ouis = DeviceOui.get()
        replies = User.reply_get()
        nas_ports = NasPort.get()
        last_seen = PostAuth.get_last_seen()

        for user in users:
            user['reply'] = cls.get_user_reply(user['username'], replies)
            nas_port = cls.user_get_port(user['username'], nas_ports)

            if nas_port is None:
                nas_port = dict()
                nas_port['nas_identifier'] = None
                nas_port['nas_port_id'] = None
                nas_port['called_station_id'] = None
                nas_port['calling_station_id'] = None

            if nas_port is not None:
                if 'calling_station_id' in nas_port:
                    user['calling_station_id'] = nas_port['calling_station_id']
                if 'calling_station_id' in nas_port:
                    user['called_station_id'] = nas_port['called_station_id']
                if 'nas_identifier' in nas_port:
                    user['nas_identifier'] = nas_port['nas_identifier']
                if 'nas_port_id' in nas_port:
                    user['nas_port_id'] = nas_port['nas_port_id']
                user['active'] = cls.user_is_active(user['username'], users)
            user['active'] = cls.user_is_active(user['username'], users)
            user['last_seen'] = cls.user_last_seen(user['username'], last_seen)

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

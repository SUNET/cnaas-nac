from flask import request
from flask import redirect
from flask import render_template

from flask_restful import Resource

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from cnaas_nac.db.user import User, PostAuth
from cnaas_nac.db.nas import NasPort


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    vlan = StringField('VLAN',  validators=[DataRequired()])
    selected = BooleanField('selectfield', default=False)
    submit = SubmitField('Add user')
    delete = SubmitField('Delete user(s)')
    enable = SubmitField('Enable user(s)')
    disable = SubmitField('Disable user(s)')


class WebAdmin(Resource):
    @classmethod
    def index(cls):
        users = User.get()
        form = UserForm()

        for user in users:
            reply = User.reply_get(_['username'])
            nas_port = NasPort.get(_['username'])

            if nas_port is None:
                nas_port['nas_identifier'] = None
                nas_port['nas_port_id'] = None

            user['reply'] = reply
            user['calling_station_id'] = nas_port['calling_station_id']
            user['nas_identifier'] = nas_port['nas_identifier']
            user['nas_port'] = nas_port['nas_port_id']
            user['active'] = User.is_enabled(user['username'])
            user['last_seen'] = PostAuth.get_last_seen(user['username'])

        if request.method == 'POST':
            result = request.form
            username = result['username']
            password = result['password']
            vlan = result['vlan']
            selected = request.form.getlist('selected')

            if 'submit' in result:
                User.add(username, password)
                User.reply_add(username, vlan)
                User.disable(username)
            elif 'delete' in result:
                for user in selected:
                    User.delete(user)
                    User.reply_delete(user)
            elif 'enable' in result:
                for user in selected:
                    User.enable(user)
            elif 'disable' in result:
                for user in selected:
                    User.disable(user)
            return redirect('/admin')

        return render_template('index.html', users=users, form=form)

from flask import request
from flask import redirect
from flask import render_template

from flask_restful import Resource

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from cnaas_nac.db.user import User, NasPort, PostAuth


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
        users = User.user_get()
        form = UserForm()

        for _ in users:
            reply = User.reply_get(_['username'])
            nas_port = ' '.join(NasPort.user_get(_['username']))
            _['reply'] = reply
            _['nas_port'] = nas_port
            _['active'] = User.user_is_enabled(_['username'])
            _['last_seen'] = PostAuth.get_last_seen(_['username'])

        if request.method == 'POST':
            result = request.form
            username = result['username']
            password = result['password']
            vlan = result['vlan']
            selected = request.form.getlist('selected')

            if 'submit' in result:
                User.user_add(username, password)
                User.reply_add(username, vlan)
                User.user_disable(username)
            elif 'delete' in result:
                for user in selected:
                    User.user_del(user)
                    User.reply_del(user)
            elif 'enable' in result:
                for user in selected:
                    User.user_enable(user)
            elif 'disable' in result:
                for user in selected:
                    User.user_disable(user)
            return redirect('/admin')

        return render_template('index.html', users=users, form=form)

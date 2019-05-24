from cnaas_nac.api.generic import build_filter, empty_result
from cnaas_nac.db.session import sqla_session
from cnaas_nac.db.user import User

from flask import request
from flask_restful import Resource
from flask import request, redirect
from flask import render_template

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    vlan = StringField('VLAN',  validators=[DataRequired()])
    submit = SubmitField('Add user')
    delete = SubmitField('Delete user')


class WebApi(Resource):
    @classmethod
    def index(cls):
        users = User.user_get()
        form = UserForm()
        errors = []

        for _ in users:
            reply = User.reply_get(_['username'])
            _['reply'] = reply

        if request.method == 'POST':
            result = request.form
            username = result['username']
            password = result['password']
            vlan = result['vlan']

            if 'submit' in result:
                User.user_add(username, password)
                User.reply_add(username, vlan)
            elif 'delete' in result:
                User.user_del(username)
                User.reply_del(username)
            return redirect('/')
        return render_template('index.html', users=users, form=form)

from flask_wtf import Form 
from wtforms import StringField, IntegerField, PasswordField, BooleanField, \
                    SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo, \
                               Email
from app.users import constants as USER
from app.users.models import User


class LoginForm(Form):
    '''Login form used by login() function in app/users/views.py'''
    email    = StringField('Email', 
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(max=128)])
    remember = BooleanField('Remember me', default=False)

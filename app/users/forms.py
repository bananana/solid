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


class SignupForm(Form):
    '''Signup form used by signup() function in app/users/views.py'''
    email            = StringField('Email',
                                   validators=[DataRequired(), Email()])
    nickname         = StringField('Nickname',
                                   validators=[DataRequired(),
                                               Regexp('[\w-]')])
    password         = PasswordField('Password', 
                                     validators=[DataRequired(), 
                                                 EqualTo('verify_password')])
    verify_password  = PasswordField('Verify password', 
                                     validators=[DataRequired()])


class EditForm(Form):
    nickname         = StringField('Nickname',
                                   validators=[Optional(), Regexp('[\w-]')])
    full_name        = StringField('Full Name',
                                   validators=[Optional()])
    email            = StringField('Email', 
                                   validators=[Optional(), Email()])
    phone            = StringField('Phone',
                                   validators=[Optional()])
    zip              = IntegerField('Zip',
                                   validators=[Optional()])
    employer         = StringField('Employer', 
                                   validators=[Optional()])
    description      = TextAreaField('Description',
                                     validators=[Optional()])
    current_password = PasswordField('Current password', 
                                     validators=[Optional()])
    new_password     = PasswordField('New password', 
                                     validators=[Optional(), 
                                                 EqualTo('verify_password')])
    verify_password  = PasswordField('Verify password', 
                                     validators=[Optional()])
    private_full_name = BooleanField('Keep full name private', default=False)

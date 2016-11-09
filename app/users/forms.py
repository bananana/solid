from flask_wtf import Form
from flask_babel import lazy_gettext as _

from wtforms import StringField, IntegerField, PasswordField, BooleanField, \
                    SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo, \
                               Email
from app.users import constants as USER
from app.users.models import User


class LoginForm(Form):
    '''Login form used by login() function in app/users/views.py'''
    login    = StringField(_('Email or Username'),
                           validators=[DataRequired()])
    password = PasswordField(_('Password'),
                             validators=[DataRequired(), Length(max=128)])
    remember = BooleanField(_('Remember me'), default=False)


class SignupForm(Form):
    '''Signup form used by signup() function in app/users/views.py'''
    email            = StringField(_('Email'),
                                   validators=[DataRequired(), Email()])
    nickname         = StringField(_('Nickname'),
                                   validators=[DataRequired(),
                                               Regexp('[\w-]')])
    full_name        = StringField(_('Full Name'),
                                   validators=[Optional()])
    password         = PasswordField(_('Password'),
                                     validators=[DataRequired(),
                                                 EqualTo('verify_password')])
    verify_password  = PasswordField(_('Verify password'),
                                     validators=[DataRequired()])


class EditForm(Form):
    nickname         = StringField(_('Nickname'),
                                   validators=[Optional(), Regexp('[\w-]')])
    full_name        = StringField(_('Full Name'),
                                   validators=[Optional()])
    email            = StringField(_('Email'),
                                   validators=[Optional(), Email()])
    phone            = StringField(_('Phone'),
                                   validators=[Optional()])
    zip              = StringField(_('Zip'),
                                   validators=[Optional()])
    employer         = StringField(_('Employer'),
                                   validators=[Optional()])
    description      = TextAreaField(_('Description'),
                                     validators=[Optional()])
    current_password = PasswordField(_('Current password'),
                                     validators=[Optional()])
    new_password     = PasswordField(_('New password'),
                                     validators=[Optional(),
                                                 EqualTo('verify_password')])
    verify_password  = PasswordField(_('Verify password'),
                                     validators=[Optional()])

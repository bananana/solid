from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _

from wtforms import StringField, IntegerField, PasswordField, BooleanField, \
                    SelectField, HiddenField, TextAreaField
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo, \
                               Email

from app import db
from app.users import constants as USER
from app.users.models import User


class LoginForm(FlaskForm):
    '''Login form used by login() function in app/users/views.py'''
    login    = StringField(_('Email or Username'),
                           validators=[DataRequired()])
    password = PasswordField(_('Password'),
                             validators=[DataRequired(), Length(max=128)])
    remember = BooleanField(_('Remember me'), default=False)


class SignupForm(FlaskForm):
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


class EditForm(FlaskForm):
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


class ResetPassword(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])


class ResetPasswordSubmit(FlaskForm):
    password = PasswordField(_('New Password'), 
                             validators=[DataRequired(), 
                             EqualTo('confirm_password')])
    confirm_password  = PasswordField(_('Confirm password'), 
                                      validators=[DataRequired()])




EmailForm = model_form(User, base_class=FlaskForm, db_session=db.session, only=(
    'email',
))

from flask_babel import lazy_gettext as _
from flask_wtf import Form 

from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

from app import db

from .models import Page


class PageForm(Form):
    name = StringField(_('Name'), validators=[DataRequired()])
    url = StringField(_('URL'), validators=[DataRequired()])
    content = TextAreaField(_('Content'), validators=[DataRequired()])
#PageForm = model_form(Page, base_class=Form, db_session=db.session, only=(
#        'name',
#        'url',
#        'content',
#))

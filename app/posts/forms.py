from app import db

from flask_babel import lazy_gettext as _
from flask_wtf import Form 
from wtforms import BooleanField
from wtforms.ext.sqlalchemy.orm import model_form

from .models import Post, Comment

PostForm = model_form(Post, base_class=Form, db_session=db.session, only=(
    'title',
    'body',
), field_args={
    'title': {'label': _('Title') },
    'body': {'label': _('Body') }
})

CommentForm = model_form(Comment, base_class=Form, db_session=db.session, only=(
    'body',
), field_args={
    'body': {'label': _('Body') }
})


class PostDeleteForm(Form):
    confirm = BooleanField(_('Are you sure?'), default=False)

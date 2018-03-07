from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms_alchemy import model_form_factory

from app.fields import MultipleFileField
from app.widgets import FileInput

from .models import Post, Comment


ModelForm = model_form_factory(FlaskForm)


class PostForm(ModelForm):
    images = MultipleFileField(
        'images',
        widget=FileInput(multiple=True, accept=['image/*']),
    )

    class Meta:
        model = Post
        only = (
            'title',
            'body',
        )
        field_args = {
            'title': {'label': _('Title')},
            'body': {'label': _('Body')}
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        only = (
            'body',
        )
        field_args = {
            'body': {'label': _('Body')}
        }


class PostDeleteForm(FlaskForm):
    confirm = BooleanField(_('Are you sure?'), default=False)

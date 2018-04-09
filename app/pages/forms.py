from flask_babel import lazy_gettext as _
from flask_wtf import Form
from wtforms_alchemy import model_form_factory

from .models import Page, PageTranslation

ModelForm = model_form_factory(Form)


class PageForm(ModelForm):
    class Meta:
        model = Page
        only = ('url',)
        field_args = {
            'url': {'label': _('URL') },
        }


class PageTranslationForm(ModelForm):
    class Meta:
        model = PageTranslation
        only = ('name', 'content')
        field_args = {
            'name': {'label': _('Name')},
            'content': {'label': _('Content')},
        }

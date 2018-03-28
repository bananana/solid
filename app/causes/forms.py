from flask_babel import lazy_gettext as _
from flask_wtf import Form
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename

from .models import Cause, CauseTranslation, Action, ActionTranslation


from wtforms_alchemy import model_form_factory
ModelForm = model_form_factory(Form)


class CauseForm(ModelForm):
	image = FileField()

	class Meta:
		model = Cause
		only = ('boss', 'location')
		field_args = {
			'location': {'label': _('Location') },
			'boss': {'label': _('Boss') },
			'image': {'label': _('Image') },
		}


class CauseTranslationForm(ModelForm):
	class Meta:
		model = CauseTranslation
		only = ('title', 'intro', 'story_content')
		field_args = {
			'title': {'label': _('Title') },
			'intro': {'label': _('Intro') },
			'story_content': {'label': _('Body') },
		}


class ActionForm(ModelForm):
	image = FileField()

	class Meta:
		model = Action
		only = ('expiration', 'link')
		field_args = {
			'expiration': {'label': _('Expiration') },
			'link': {'label': _('Link') },
			'image': {'label': _('Image') },
		}


class ActionTranslationForm(ModelForm):
	class Meta:
		model = ActionTranslation
		only = ('title', 'summary', 'description',)
		field_args = {
			'title': {'label': _('Title') },
			'summary': {'label': _('Summary') },
			'description': {'label': _('Description') },
		}

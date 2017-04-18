from app import db

from flask_babel import lazy_gettext as _
from flask_wtf import Form 
from wtforms.ext.sqlalchemy.orm import model_form

from .models import Cause, CauseTranslation, Action


CauseForm = model_form(Cause, base_class=Form, db_session=db.session, only=(
	'boss',
	'location',
	'image',
), field_args={
    'location': {'label': _('Location') },
    'boss': {'label': _('Boss') },
    'image': {'label': _('Image') },
})

CauseTranslationForm = model_form(
	CauseTranslation, base_class=Form, db_session=db.session, only=(
		'title',
		'intro',
		'story_heading',
		'story_content'
	), field_args={
		'title': {'label': _('Title') },
		'intro': {'label': _('Intro') },
		'story_heading': {'label': _('Heading') },
		'story_content': {'label': _('Body') },
	}
)

ActionForm = model_form(Action, base_class=Form, db_session=db.session, only=(
	'title',
	'summary',
	'description',
	'expiration',
	'link',
), field_args={
    'title': {'label': _('Title') },
    'summary': {'label': _('Summary') },
    'description': {'label': _('Description') },
    'expiration': {'label': _('Expiration') },
    'link': {'label': _('Link') },
})

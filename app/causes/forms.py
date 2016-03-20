from app import db

from flask_wtf import Form 
from wtforms.ext.sqlalchemy.orm import model_form

from .models import Cause

CauseForm = model_form(Cause, base_class=Form, db_session=db.session, only=(
	'title',
	'boss',
	'location',
	'image',
	'story_heading',
	'story_content'
))
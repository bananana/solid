from app import db

from flask_wtf import Form 
from wtforms.ext.sqlalchemy.orm import model_form

from .models import Page, PageTranslation


PageForm = model_form(Page, base_class=Form, db_session=db.session, only=(
        'url',
))

PageTranslationForm = model_form(
        PageTranslation, base_class=Form, db_session=db.session, only=(
                'name',
                'content',
        )
)

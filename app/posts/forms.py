from app import db

from flask_wtf import Form 
from wtforms.ext.sqlalchemy.orm import model_form

from .models import Post, Comment

PostForm = model_form(Post, base_class=Form, db_session=db.session, only=(
    'title',
    'body',
))

CommentForm = model_form(Comment, base_class=Form, db_session=db.session, only=(
    'body',
))

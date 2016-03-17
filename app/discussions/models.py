import datetime

from app import db
from app.mixins import CRUDMixin 

from app.causes.models import Cause
from app.users.models import User


class Post(CRUDMixin, db.Model):
    __tablename__ = 'discussions_post'
    id            = db.Column(db.Integer, primary_key=True)

    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    cause         = db.relationship('Cause', backref=db.backref('posts', lazy='dynamic'))

    title         = db.Column(db.String(128))
    body          = db.Column(db.Text)
    author_id     = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    author        = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))

    created_on    = db.Column(db.DateTime)


    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = datetime.datetime.utcnow()

        return super(Post, self).save(*args, **kwargs)

    def __repr__(self):
       return '<Post %r>' % (self.title)


class Comment(CRUDMixin, db.Model):
    __tablename__ = 'discussions_comment'
    id            = db.Column(db.Integer, primary_key=True)
    post_id       = db.Column(db.Integer, db.ForeignKey('discussions_post.id'))
    reply_to_id   = db.Column(db.Integer, db.ForeignKey('discussions_comment.id'))
    body          = db.Column(db.Text)
    author        = db.Column(db.Integer, db.ForeignKey('users_user.id'))

    def __repr__(self):
        return '<Demand %r' % (self.title)

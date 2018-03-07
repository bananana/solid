import datetime

from app import db, uploaded_images
from app.mixins import CRUDMixin

from app.causes.models import Cause
from app.users.models import User


class Post(CRUDMixin, db.Model):
    __tablename__ = 'discussions_post'
    id            = db.Column(db.Integer, primary_key=True)

    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    cause         = db.relationship('Cause', backref=db.backref(
        'posts', lazy='dynamic', order_by="Post.created_on.desc()"
    ))

    body          = db.Column(db.Text, nullable=False)
    author_id     = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    author        = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))

    # FIXME deprecated
    summary       = db.Column(db.Text)
    title         = db.Column(db.String(128))

    created_on    = db.Column(db.DateTime)


    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = datetime.datetime.utcnow()

        return super(Post, self).save(*args, **kwargs)

    def __repr__(self):
        return '<Post "%r">' % (self.body[:20])


class PostImage(CRUDMixin, db.Model):
    __tablename__ = 'discussions_postimage'
    id            = db.Column(db.Integer, primary_key=True)

    post_id       = db.Column(db.Integer, db.ForeignKey('discussions_post.id'))
    post          = db.relationship('Post', backref=db.backref(
        'images', lazy='dynamic'
    ))

    image         = db.Column(db.String(128))

    @property
    def image_url(self):
        return uploaded_images.url(self.image)

    created_on    = db.Column(db.DateTime)

    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = datetime.datetime.utcnow()

        return super(PostImage, self).save(*args, **kwargs)

    def __repr__(self):
       return '<PostImage "%r">' % (self.id)


class Comment(CRUDMixin, db.Model):
    __tablename__ = 'discussions_comment'

    id            = db.Column(db.Integer, primary_key=True)

    created_on    = db.Column(db.DateTime)

    post_id       = db.Column(db.Integer, db.ForeignKey('discussions_post.id'))
    post          = db.relationship('Post', backref=db.backref('comments', lazy='dynamic'))

    reply_to_id   = db.Column(db.Integer, db.ForeignKey('discussions_comment.id'))
    reply_to      = db.relationship('Comment', remote_side=[id],
                                    backref=db.backref('replies', lazy='dynamic'))

    body          = db.Column(db.Text)
    author_id     = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    author        = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = datetime.datetime.utcnow()

        return super(Comment, self).save(*args, **kwargs)

    def __repr__(self):
        return '<Comment @{0.id} on "{0.post.title}">'.format(self)

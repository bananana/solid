import datetime

from app import db
from app.mixins import CRUDMixin 

from slugify import slugify

supporters = db.Table('causes_supporters',
    db.Column('cause_id', db.Integer, db.ForeignKey('causes_cause.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
)

creators = db.Table('causes_creators',
    db.Column('cause_id', db.Integer, db.ForeignKey('causes_cause.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
)


class Cause(CRUDMixin, db.Model):
    __tablename__ = 'causes_cause'
    id            = db.Column(db.Integer, primary_key=True)
    actions       = db.relationship('Action', backref='assigned_campaign', lazy='dynamic')
    demands       = db.relationship('Demand', backref='assigned_campaign', lazy='dynamic')

    title         = db.Column(db.String(128))
    slug          = db.Column(db.String(128))
    boss          = db.Column(db.String(128))
    created_on    = db.Column(db.DateTime)
    location      = db.Column(db.String(128))

    creators      = db.relationship('User', secondary=creators,
                                    backref='causes_created', lazy='dynamic')
    supporters    = db.relationship('User', secondary=supporters,
                                    backref='causes_supported', lazy='dynamic')

    video         = db.Column(db.String(128))
    image         = db.Column(db.String(128))
    story_heading = db.Column(db.String(128))
    story_content = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))

        if not 'created_on' in kwargs:
            kwargs['created_on'] = datetime.datetime

        super(Cause, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Cause %r>' % (self.title)    


class Action(CRUDMixin, db.Model):
    __tablename__ = 'causes_action'
    id            = db.Column(db.Integer, primary_key=True)
    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    title         = db.Column(db.String(128))
    heading       = db.Column(db.String(64))
    description   = db.Column(db.Text)
    supporters    = db.Column(db.Integer)
    expiration    = db.Column(db.DateTime)

    def __init__(self, title=None, heading=None, description=None, supporters=None,
                 expiration=None):
        self.title = title
        self.heading = heading
        self.description = description
        self.supporters = supporters
        self.expiration = expiration

    def __repr__(self):
       return '<Action %r>' % (self.title)

class Demand(CRUDMixin, db.Model):
    __tablename__ = 'causes_demand'
    id            = db.Column(db.Integer, primary_key=True)
    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    title         = db.Column(db.String(64))
    resolved      = db.Column(db.Boolean)
    description   = db.Column(db.Text)

    def __int__(self, title=None, resolved=False, description=None):
        self.title = title
        self.resolved = resolved
        self.description = description

    def __repr__(self):
        return '<Demand %r' % (self.title)

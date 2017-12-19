from app import db, bcrypt
from app.mixins import CRUDMixin 
from app.causes.models import cause_supporters, cause_creators, action_supporters
from flask_login import UserMixin
from random import randint


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'users_user'
    id          = db.Column(db.Integer, primary_key=True)
    social_id   = db.Column(db.String(64), unique=True)
    is_admin    = db.Column(db.Boolean)
    last_login  = db.Column(db.DateTime)
    nickname    = db.Column(db.String(64), index=True, unique=True)
    password    = db.Column(db.String(128))
    full_name   = db.Column(db.String(64))
    initials    = db.Column(db.String(8))
    color       = db.Column(db.String(7))
    email       = db.Column(db.String(128), index=True)
    phone       = db.Column(db.Integer, index=True)
    zip         = db.Column(db.String(5), index=True)
    employer    = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)

    locale      = db.Column(db.String(2))

    supports    = db.relationship('Cause', 
                                  secondary=cause_supporters,
                                  backref='causes_supported', 
                                  viewonly=True,
                                  lazy='dynamic')

    created     = db.relationship('Cause',
                                  secondary=cause_creators,
                                  viewonly=True,
                                  backref='causes_created',
                                  lazy='dynamic')

    actions     = db.relationship('Action',
                                  secondary=action_supporters,
                                  viewonly=True,
                                  backref='actions_supported',
                                  lazy='dynamic')

    def __init__(self, social_id=None, is_admin=False, nickname=None, 
                 password=None, full_name=None, initials=None, 
                 color='#e5e5e5', email=None, phone=None, zip=None, employer=None, 
                 description=None):
        self.social_id = social_id
        self.is_admin = is_admin
        self.nickname = nickname
        self.password = password
        self.full_name = full_name
        self.initials = initials 
        self.color = color
        self.email = email
        self.phone = phone
        self.zip = zip
        self.employer = employer
        self.description = description

    def set_password(self,  password):
        '''Hash the provided password with bcrypt and push it to the database.
        '''
        password_hash = bcrypt.generate_password_hash(password)
        self.update(**{'password': password_hash})

    def is_valid_password(self, password):
        '''Check password hash with bcrypt. Return True if password is correct,
        otherwise returns False.
        '''
        if self.password:
            return bcrypt.check_password_hash(self.password, password)
        else:
            return False

    def generate_initials(self):
        if self.full_name:
            initials = ''.join([n[0] for n in self.full_name.split()])
        elif self.nickname:
            initials = self.nickname[:1].capitalize()
        else:
            initials = '??'
        self.update(**{'initials': initials})

    def generate_color(self):
        rand_color = '#%06x' % randint(0, 0xFFFFFF)
        self.update(**{'color': rand_color})

    def set_locale(self, loc):
        self.update(**{'locale': loc})

    def is_supporting(self, cause):
        return self.supports.filter(cause_supporters.c.cause_id == cause.id).count() > 0

    def support(self, cause):
        if not self.is_supporting(cause):
            cause.supporters.append(self)
    
    def unsupport(self, cause):
        if self.is_supporting(cause):
            cause.supporters.remove(self)

    def actions_per_cause(self, cause):
        return self.actions.filter_by(cause_id=cause.id)

    @property
    def name(self):
        if self.full_name:
            return self.full_name
        else:
            return self.nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname) 

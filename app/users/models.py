from app import db, bcrypt
from app.mixins import CRUDMixin 
from flask.ext.login import UserMixin


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = 'users_user'
    id          = db.Column(db.Integer, primary_key=True)
    last_login  = db.Column(db.DateTime)
    nickname    = db.Column(db.String(64), index=True, unique=True)
    password    = db.Column(db.String(128))
    full_name   = db.Column(db.String(64))
    initials    = db.Column(db.String(8))
    email       = db.Column(db.String(128), index=True)
    phone       = db.Column(db.Integer, index=True)
    zip         = db.Column(db.Integer, index=True)
    employer    = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)

    def __init__(self, nickname=None, password=None, full_name=None,
                 initials=None, email=None, phone=None, zip=None,
                 employer=None, description=None):
        self.nickname = nickname
        self.password = password
        self.full_name = full_name
        # self.initials = ''.join([n[0] for n in full_name.split()])
        self.initials = initials
        self.email = email
        self.phone = phone
        self.zip = zip
        self.employer = employer
        self.description = description

    def __repr__(self):
        return '<User %r>' % (self.nickname)    

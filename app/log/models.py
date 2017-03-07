from pytz import timezone
from datetime import datetime

from sqlalchemy_utils import generic_relationship

from app import db


class LogEventType(db.Model):
    __tablename__ = 'log_event_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    EVENT_TYPES = {
        'cause_add': 1,
        'cause_edit': 2,
        'cause_support': 3,
        'cause_milestone': 4,
        'action_add': 5,
        'action_support': 6,
        'action_comment': 7,
        'post_add': 8,
        'post_reply': 9,
    }

    @staticmethod
    def seed_event_types():
        for name, id in LogEventType.EVENT_TYPES.iteritems():
            event_type = LogEventType(id=id, name=name)
            db.session.add(event_type)
        db.session.commit()

    def __repr__(self):
        return '<LogEventType %r>' % self.name


class LogEvent(db.Model):
    __tablename__ = 'log_events'
    id = db.Column(db.Integer, primary_key=True)

    event_type_id = db.Column(db.Integer, db.ForeignKey('log_event_types.id'))
    event_type = db.relationship('LogEventType', backref=db.backref('events', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    user = db.relationship('User', backref=db.backref('events', lazy='dynamic'))

    item_type = db.Column(db.Unicode(255))
    item_id = db.Column(db.Integer)
    item = generic_relationship(item_type, item_id)
    
    logged_at = db.Column(db.DateTime(), default=datetime.now(timezone('UTC')))

    @staticmethod
    def _log(name, item, user=None):
        event = LogEvent(event_type_id=LogEventType.EVENT_TYPES[name], user=user, item=item)
        db.session.add(event)
        db.session.commit()

    def __repr__(self):
        return '<LogEvent %r on %r>' % (self.item_type, self.logged_at)

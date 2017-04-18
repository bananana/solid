import datetime

from slugify import slugify
from sqlalchemy_i18n import Translatable, translation_base

from app import db, app
from app.mixins import CRUDMixin 


cause_creators = db.Table('causes_cause_creators',
    db.Column('cause_id', db.Integer, db.ForeignKey('causes_cause.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
)

cause_supporters = db.Table('causes_cause_supporters',
    db.Column('cause_id', db.Integer, db.ForeignKey('causes_cause.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
)


class Cause(CRUDMixin, db.Model, Translatable):
    __tablename__ = 'causes_cause'

    __translatable__ = {
        'locales': app.config['SUPPORTED_LANGUAGES']
    }

    id            = db.Column(db.Integer, primary_key=True)
    demands       = db.relationship('Demand', backref='assigned_campaign', lazy='dynamic')

    slug          = db.Column(db.String(128), nullable=False)
    boss          = db.Column(db.String(128))
    created_on    = db.Column(db.DateTime)
    location      = db.Column(db.String(128))

    creators      = db.relationship('User', secondary=cause_creators,
                                    backref='causes_created', lazy='dynamic')
    supporters    = db.relationship('User', secondary=cause_supporters,
                                    backref='causes_supported', lazy='dynamic')

    video         = db.Column(db.String(128))
    image         = db.Column(db.String(128))

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            # even if cause title changes subsequently, the slug should remain
            # the same
            self.slug = slugify(unicode(self.title))

        if not self.created_on:
            self.created_on = datetime.datetime.utcnow()

        return super(Cause, self).save(*args, **kwargs)

    @property
    def action_supporters(self):
        # set of users supporting actions on this cause
        from app.users.models import User
        return User.query.filter(
            User.actions_supported.any(
                Action.id.in_(a.id for a in self.actions.all())
            )
        )

    @property
    def count_action_supports(self):
        from app.users.models import User
        query = action_supporters.count(
            whereclause=action_supporters.c.action_id.in_(
                a.id for a in self.actions.all()
            )
        )
        result = db.engine.execute(query)
        return result.fetchone()[0]

    def __repr__(self):
        return '<Cause %r>' % (self.title)    


class CauseTranslation(translation_base(Cause)):
    __tablename__ = 'causes_cause_translation'

    title         = db.Column(db.String(40))
    story_heading = db.Column(db.String(128))
    story_content = db.Column(db.Text)
    intro         = db.Column(db.Text(180))

    def __repr__(self):
        return '<Cause %r>' % (self.title)    


action_supporters = db.Table('causes_action_supporters',
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
    db.Column('action_id', db.Integer, db.ForeignKey('causes_action.id')),
)


class Action(CRUDMixin, db.Model):
    __tablename__ = 'causes_action'
    id            = db.Column(db.Integer, primary_key=True)

    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    cause         = db.relationship('Cause', backref=db.backref(
        'actions', lazy='dynamic', order_by='Action.id.desc()'
    ))

    title         = db.Column(db.String(128), nullable=False)

    summary       = db.Column(db.Text)
    description   = db.Column(db.Text)

    link          = db.Column(db.String(500))

    supporters    = db.relationship('User', secondary=action_supporters,
                                    backref='actions_supported', lazy='dynamic')

    expiration    = db.Column(db.DateTime)

    def __repr__(self):
       return '<Action %r>' % (self.title)


class Demand(CRUDMixin, db.Model):
    __tablename__ = 'causes_demand'
    id            = db.Column(db.Integer, primary_key=True)
    cause_id      = db.Column(db.Integer, db.ForeignKey('causes_cause.id'))
    title         = db.Column(db.String(64))
    resolved      = db.Column(db.Boolean)
    description   = db.Column(db.Text)

    def __repr__(self):
        return '<Demand %r' % (self.title)

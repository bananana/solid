from app import app, db, bcrypt
from app.mixins import CRUDMixin 
from app.causes.models import cause_supporters, action_supporters
from flask_login import UserMixin
from random import randint
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


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
        return self.causes_supports.filter(cause_supporters.c.cause_id == cause.id).count() > 0

    def support(self, cause):
        if not self.is_supporting(cause):
            cause.supporters.append(self)
    
    def unsupport(self, cause):
        if self.is_supporting(cause):
            cause.supporters.remove(self)

    def actions_per_cause(self, cause):
        return self.actions.filter_by(cause_id=cause.id)

    def notifications(self):
        from app.log.models import LogEvent, LogEventType, LogEventViewed
        from app.causes.models import Cause, Action
        from app.posts.models import Post, Comment

        user_causes = self.causes_supports
        
        user_cause_actions = Action.query.filter(Action.cause_id.in_(
            [c.id for c in user_causes.all()]
        ))

        user_cause_posts = Post.query.filter(Post.cause_id.in_(
            [c.id for c in user_causes.all()]
        ))

        user_cause_post_comments = Comment.query.filter(Comment.post_id.in_(
            [p.id for p in user_cause_posts.all()]
        ))

        return LogEvent.query.filter(
            (
                (LogEvent.event_type_id.in_([LogEventType.EVENT_TYPES[e] for e in [
                    'cause_add',
                    'cause_support'
                ]]))
                & (LogEvent.item_id.in_([c.id for c in user_causes.all()]))
            )
            | (
                (LogEvent.event_type_id.in_([LogEventType.EVENT_TYPES[e] for e in [
                    'action_add',
                    'action_support'
                ]]))
                & (LogEvent.item_id.in_([a.id for a in user_cause_actions.all()]))
            )
            | (
                (LogEvent.event_type_id == LogEventType.EVENT_TYPES['post_add'])
                & (LogEvent.item_id.in_([p.id for p in user_cause_posts.all()]))
            )
            | (
                (LogEvent.event_type_id == LogEventType.EVENT_TYPES['post_reply'])
                & (LogEvent.item_id.in_([c.id for c in user_cause_post_comments.all()]))
            )
        )\
            .order_by(LogEvent.logged_at.desc())\
            .outerjoin(LogEventViewed)\
            .add_column(db.func.count(LogEventViewed.id))\
            .group_by(LogEvent.id)

    def get_token(self, expiration=1800):
        s = Serializer(app.config['SECRET_KEY']) 
        return s.dumps({'user': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        id = data.get('user')
        if id:
            return User.query.get(id)
        return None

    @property
    def name(self):
        if self.full_name:
            return self.full_name
        else:
            return self.nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname) 

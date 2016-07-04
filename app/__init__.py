from os import environ

from flask import Flask, render_template

app = Flask(__name__)

if environ.get('FLASK_CONFIG', None) is None:
    environ['FLASK_CONFIG'] = 'config/local.py'

app.config.from_envvar('FLASK_CONFIG')

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext.login import LoginManager
lm = LoginManager()
lm.init_app(app)

from flask.ext.bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask.ext.misaka import Misaka
mikasa = Misaka(app)

from flask.ext.mail import Mail
mail = Mail(app)

# Register blueprints
from app.users.views import mod as usersModule
app.register_blueprint(usersModule)
lm.login_view = 'users.login'

from app.causes.views import mod as causesModule
app.register_blueprint(causesModule)

from app.styleguide.views import mod as styleguideModule
app.register_blueprint(styleguideModule)

from app.posts.views import mod as postsModule
app.register_blueprint(postsModule)

from flask_dance.contrib.twitter import make_twitter_blueprint
twitter_blueprint = make_twitter_blueprint(
    redirect_to   = 'users.authorize_twitter' 
)
app.register_blueprint(twitter_blueprint, url_prefix='/login')

from flask_dance.contrib.google import make_google_blueprint 
google_blueprint = make_google_blueprint(
    scope         = ['profile', 'email'],
    redirect_to   = 'users.authorize_google'
)
app.register_blueprint(google_blueprint, url_prefix='/login')

from flask_dance.contrib.facebook import make_facebook_blueprint 
facebook_blueprint = make_facebook_blueprint(
    scope         = ['email'],
    redirect_to   = 'users.authorize_facebook'
)
app.register_blueprint(facebook_blueprint, url_prefix='/login')


# HTTP errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Default app view, same for all modules
from app.causes.views import cause_required, multi_cause
@app.route('/')
@cause_required
@multi_cause
def index():
    '''Home page of the app. Nothing much here.'''
    return render_template('index.html')


# Logging 
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('../tmp/app.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Application started up!')

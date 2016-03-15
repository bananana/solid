from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt
from flask_dance.contrib.github import make_github_blueprint 
from flask_dance.contrib.twitter import make_twitter_blueprint


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
bcrypt = Bcrypt(app)


# Register blueprints
from app.users.views import mod as usersModule
app.register_blueprint(usersModule)
lm.login_view = 'users.login'

from app.causes.views import mod as causesModule
app.register_blueprint(causesModule)

from app.styleguide.views import mod as styleguideModule
app.register_blueprint(styleguideModule)

github_blueprint = make_github_blueprint(
    client_id     = '838a5146c0c02c49b6b1',
    client_secret = '5ec8fef4e5ad9c0340e1c382f302a9fd4ab72b4b',
    redirect_to   = 'users.authorize_github'
)
app.register_blueprint(github_blueprint, url_prefix='/login')

twitter_blueprint = make_twitter_blueprint(
    api_key       = 'MXRHGhjB19kPKLd3G0hywzqAc',
    api_secret    = 'Fe7ckjmAhyf1fcuhmDTxb2CAUWs9Ms66KbTwsYy5nyW4vlZf9g',
    redirect_to   = 'users.authorize_twitter'
)
app.register_blueprint(twitter_blueprint, url_prefix='/login')


# HTTP errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Default app view, same for all modules
@app.route('/')
@app.route('/index')
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

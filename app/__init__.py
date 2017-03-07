from os import environ

from flask import Flask, render_template, flash, redirect, url_for

app = Flask(__name__)

if environ.get('FLASK_CONFIG', None) is None:
    environ['FLASK_CONFIG'] = 'config/local.py'

app.config.from_envvar('FLASK_CONFIG')


from flask_babel import Babel

babel = Babel(app)

@babel.localeselector
def get_locale():
    """ Use the browser's language preferences to select available translation """
    '''
    translations = [str(translation) for translation in
                    babel.list_translations()]
    return request.accept_languages.best_match(translations)
    '''
    return 'en'


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask_login import LoginManager
lm = LoginManager()
lm.init_app(app)

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask_misaka import Misaka
mikasa = Misaka(app)

from flask_mail import Mail
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

from app.pages.views import mod as pagesModule
app.register_blueprint(pagesModule)

from app.admin.views import mod as adminModule
app.register_blueprint(adminModule)

from app.log.views import mod as logModule
app.register_blueprint(logModule)

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


# Context processors

@app.context_processor
def config_vars():
    return dict(
        debug=app.debug, 
        site_name=app.config['SITE_NAME'],
        server_name=app.config['SERVER_NAME'],
        fb_app_id=app.config['FACEBOOK_OAUTH_CLIENT_ID']
    )


# HTTP errors

from flask import request
from app.pages.models import Page

@app.errorhandler(404)
def not_found_error(error):
    # Look for a Page with this URL
    page = Page.query.filter_by(url=request.path).first()

    if page:
        return render_template('pages/page.html', page=page)

    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# views

from app.causes.views import cause_required
@app.route('/')
@cause_required
def index():
    '''Home page of the app. Nothing much here.'''
    return redirect(url_for('causes.index'))


from app.contact.forms import ContactForm
from app.email import send_email

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        recipients = [app.config['CONTACT_EMAIL'],]

        if form.send_to_self.data:
            recipients += [form.email.data,]

        send_email(
            'Solid inquiry via website',
            recipients,
            {'name': form.name.data, 'body': form.message.data, 
             'email': form.email.data},
            'email/contact.txt'
        )

        flash('Your message has been sent!.', 'success')
        return redirect(url_for('.contact'))

    return render_template('contact.html', form=form)

# logging 

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('../tmp/app.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Application started up!')

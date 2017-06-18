from datetime import datetime

from flask import (Blueprint, render_template, url_for, redirect, session,
                   request, g, flash, abort)
from flask_login import login_user, logout_user, current_user, login_required
from flask_dance.contrib.google import google 
from flask_dance.contrib.twitter import twitter
from flask_dance.contrib.facebook import facebook
from flask_dance.consumer import oauth_authorized
from flask_babel import refresh, get_locale, gettext as _

from slugify import slugify

from app import app, db, lm, babel
from app.email import send_email

from . import constants as USER
from .forms import LoginForm, SignupForm, EditForm, EmailForm
from .models import User
from ..decorators import no_email_required

from app.posts.models import Post, Comment

import re

#: Module blueprint
mod = Blueprint('users', __name__)


@lm.user_loader
def load_user(id):
    '''Load the user. Required for using Flask login extention.
    '''
    return User.query.get(int(id))


@mod.before_request
def before_request():
    '''Push the current user into Flask's g global. If user is authenticated,
    updated their last login date/time.
    '''
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_login = datetime.utcnow()
        g.user.save()


@no_email_required
@mod.route('/email', methods=['GET', 'POST'])
def set_email():
    form = EmailForm(request.form)

    user = current_user

    if form.validate_on_submit():
        form.populate_obj(user)
        user.update()
        flash('Email updated successfully', 'success')
        return redirect(
            session.pop('next', False)
            or url_for('.user', nickname=nickname)
        )

    return render_template('users/email.html', form=form, user=user)


@oauth_authorized.connect
def logged_in(blueprint, token):
    return redirect(request.args.get('next') or url_for('index'))


@babel.localeselector
def get_locale():
    '''This method has to return a language code that determines the app's 
    display language. lang_code session variable is used to store such a code.
    If user is unauthenticated it is set to whatever their browser locale is.
    It can be changed with the language select widget which uses the 
    translate() method implemented in this file. Alternatively, if a user is 
    authenticated, they can set their language preferences in their profile 
    settings.
    '''

    if session.get('lang_code') is None:
        if current_user.is_authenticated and current_user.locale is not None:
            # If user is logged in use their language preferences
            session['lang_code'] = current_user.locale
        else:
            # Use the browser's language preferences to select available translation
            session['lang_code'] = request.accept_languages.best_match(
                app.config['SUPPORTED_LANGUAGES'].keys()
            )
    return session['lang_code']


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Get basic user info and sign them up.
    '''
    # If user is already logged in, redirect them to their profile
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('.user', nickname=g.user.nickname))

    form = SignupForm()
    if form.validate_on_submit():
        #: Check if nickname already exists
        nickname = User.query.filter_by(nickname=form.nickname.data).first()
        if nickname is None:
            new_user = User.create(**{
                'email'    : form.email.data,
                'nickname' : form.nickname.data,
                'full_name': form.full_name.data
            })
            new_user.set_password(form.password.data)
            new_user.generate_initials()
            new_user.generate_color()
            new_user.set_locale(session['lang_code'])
            login_user(new_user)
            send_email('Welcome to {0}'.format(app.config['SITE_NAME']),
                       [new_user.email,],
                       {'user': new_user},
                       'email/user_signup.txt')
            return redirect(
                request.args.get('next') 
                or session.pop('next', False)
                or url_for('index')
            )
        else:
            flash(_('Nickname already exists, please pick a different one.'), 'error')

    return render_template('users/signup.html', form=form)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    '''Login user after checking credentials, which are their email and password.
    '''
    # If user is already logged in, redirect them to their profile
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.args.get('next'):
        session['next'] = request.args.get('next')

    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        remember = bool(form.remember.data)

        #: Query the database with the provided credentials 
        email = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])+")
        match = email.match(login)
        if match:
            user_query = User.query.filter_by(email=login).first()
        else:
            user_query = User.query.filter_by(nickname=login).first()

        if user_query is not None and \
           user_query.is_valid_password(form.password.data):
            login_user(user_query, remember=remember)
            return redirect(
                request.args.get('next') 
                or session.pop('next', False)
                or url_for('index')
            )
        else:
            flash(_('Email or Password is invalid'), 'error')

    return render_template('users/login.html', form=form)


@mod.route('/authorize/google')
def authorize_google():
    '''Login using OAuth and a Google account.
    '''
    # Prevent unauthorized users from getting here
    if not google.authorized:
        return redirect(url_for('google.login'))

    # Get the response from google and get the necessary user info
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    social_id = str(resp.json()['id'])
    nickname = '_'.join([str(resp.json()['name']['givenName']), 
                         str(resp.json()['name']['familyName'])])
    full_name = ' '.join([str(resp.json()['name']['givenName']), 
                          str(resp.json()['name']['familyName'])])
    email = str(resp.json()['emails'][0]['value'])
    
    #: Query the database to see if user already exists
    user_query = User.query.filter_by(social_id=social_id).first()

    if user_query is None: 
        #: User is not in database, create a new one
        new_user = User.create(**{
            'social_id' : social_id,
            'nickname'  : nickname,
            'email'     : email
        })
        new_user.generate_initials()
        new_user.generate_color()
        login_user(new_user)
    else:
        login_user(user_query)

    return redirect(
        request.args.get('next') 
        or session.get('next', False)
        or url_for('index')
    )


@mod.route('/authorize/twitter')
def authorize_twitter():
    '''Login using OAuth and a Twitter account.
    '''
    # Prevent unauthorized users from getting here
    if not twitter.authorized:
        return redirect(url_for('twitter.login'))

    # Get the response from twitter and get the necessary user info
    resp = twitter.get('account/settings.json')
    assert resp.ok
    #return str(resp.json())
    #social_id = str(resp.json()['woeid'])
    nickname = str(resp.json()['screen_name'])
    social_id = nickname

    # Twitter does not allow to get user email, unless we request
    # elevated permissions:
    # https://dev.twitter.com/rest/reference/get/account/verify_credentials
    #email = str(resp.json()['email']

    #: Query the database to see if user already exists
    user_query = User.query.filter_by(social_id=social_id).first()

    if user_query is None: 
        #: User is not in database, create a new one
        new_user = User.create(**{
            'social_id' : social_id,
            'nickname'  : nickname,
            #'email'     : email
        })
        new_user.generate_initials()
        new_user.generate_color()
        login_user(new_user)
    else:
        login_user(user_query)
    return redirect(
        request.args.get('next') 
        or session.get('next', False)
        or url_for('index')
    )


@mod.route('/authorize/facebook')
def authorize_facebook():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))

    r = facebook.get('/v2.5/me?fields=name,email,link,picture,id').json()

    #: Query the database to see if user already exists
    user_query = User.query.filter_by(social_id=r['id']).first()

    if user_query is None: 
        #: User is not in database, create a new one
        new_user = User.create(**{
            'social_id' : r['id'],
            'nickname'  : slugify(r['name']),
            'email'     : r.get('email', ''),
            'full_name' : r['name'],
            'initials'  : "".join([w[0] for w in r['name'].split(' ')]).upper()

        })
        new_user.generate_initials()
        new_user.generate_color()
        login_user(new_user)
    else:
        login_user(user_query)
    return redirect(
        request.args.get('next') 
        or session.get('next', False)
        or url_for('index')
    )


@mod.route('/logout')
def logout():
    '''Simply logout the user and go back to index page.
    '''
    logout_user()
    flash(_('You have been logged out successfully'), 'success')
    return redirect(url_for('index'))


@mod.route('/user/<nickname>')
@login_required
def user(nickname):
    '''Display user profile.
    '''
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()
    
    if user is None:
        abort(404)

    #: Causes supported by user being viewed
    supported_causes = user.supports.all()

    # Generate feed
    user_posts = Post.query.filter_by(author_id=user.id).all()
    user_comments = Comment.query.filter_by(author_id=user.id).all()
    feed = user_posts + user_comments
    feed = sorted(feed, key=lambda item: item.created_on)

    return render_template('users/index.html', user=user, feed=feed[::-1])


@mod.route('/user/<nickname>/edit', methods=['GET', 'POST'])
@login_required
def edit(nickname):
    '''User profile editing.
    '''
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()

    if user is None:
        abort(404)

    if current_user.id is not user.id and not current_user.is_admin:
        abort(403)

    # Serve regular form when user edits their own profile
    form = EditForm()

    if form.validate_on_submit():
        #: A list of all the form data, including empty fields
        complete_form_data = form.data

        # Delete password fields from the list because password has to be 
        # processed separately anyway
        del(complete_form_data['verify_password'], 
            complete_form_data['current_password'], 
            complete_form_data['new_password'])

        # Remove empty fields from list
        form_data = {k:v for k,v in complete_form_data.iteritems() if not v == ''}
        # Set the password if it was submitted
        if form.new_password.data:
            user.set_password(form.new_password.data)

        user.update(**form_data)
        user.generate_initials()
        flash('User updated successfully', 'success')
        return redirect(url_for('.user', nickname=nickname))
    else:
        # Create a list of field keys, remove password fields from it because the
        # password has to be processed separately.
        fields = form.data.keys()
        fields.remove('current_password')
        fields.remove('new_password') 
        fields.remove('confirm_password')

        # Set default form field values based on current values in the 
        # database for user being edited.
        for field in fields:
            setattr(getattr(form, field), 'default', getattr(user, field))
        form.process()

    return render_template('users/edit.html', user=user, form=form)


@mod.route('/user/<nickname>/delete')
@login_required
def delete(nickname):
    '''Delete user.
    '''
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()

    if user is None:
        abort(404)

    if current_user.id is not user.id and not current_user.is_admin:
        abort(403)
    
    if current_user.id is user.id:
        logout_user()

    user.delete()
    flash('User deleted successfully', 'success')

    return redirect(url_for('index')) 


@mod.route('/translate', methods=['POST'])
def translate():
    '''Change app's display language using the language select widget.
    The widget's logic is located in /app/static/js/translate.js
    '''
    if request.method == 'POST' \
    and request.form['lang_code'] in tuple(app.config['SUPPORTED_LANGUAGES'].keys()):
        session['lang_code'] = request.form['lang_code'] 
        if current_user.is_authenticated:
            current_user.locale = session['lang_code']
            current_user.update()
    return ('', 204)

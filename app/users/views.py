from datetime import datetime
from flask import Blueprint, render_template, url_for, redirect, session, \
                  request, g, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_dance.contrib.google import google 
from flask_dance.contrib.twitter import twitter
from app import app, db, lm
from app.users import constants as USER
from app.users.forms import LoginForm, SignupForm, EditForm
from app.users.models import User

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


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Get basic user info and sign them up.
    '''
    # If user is already logged in, redirect them to their profile
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.user', nickname=g.user.nickname))

    form = SignupForm()
    if form.validate_on_submit():
        new_user = User.create(**{
            'email'    : form.email.data,
            'nickname' : form.nickname.data,
        })
        new_user.set_password(form.password.data)
        login_user(new_user)
        return redirect(url_for('.user', nickname=g.user.nickname))

    return render_template('users/signup.html', form=form)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    '''Login user after checking credentials, which are their email and password.
    '''
    # If user is already logged in, redirect them to their profile
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.user', nickname=g.user.nickname))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        remember = bool(form.remember.data)

        #: Query the database with the provided credentials 
        user_query = User.query.filter_by(email=email).first()

        if user_query is not None and \
           user_query.is_valid_password(form.password.data):
            login_user(user_query, remember=remember)
            return redirect(request.args.get('next') or 
                            url_for('.user', nickname=g.user.nickname))
        else:
            flash('Email or Password is invalid', 'error')

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
        login_user(new_user)
        return redirect(url_for('.user', nickname=g.user.nickname))
    else:
        login_user(user_query)
        return redirect(url_for('.user', nickname=g.user.nickname))


@mod.route('/authorize/twitter')
def authorize_twitter():
    '''Login using OAuth and a Twitter account.
    '''
    # Prevent unauthorized users from getting here
    if not twitter.authorized:
        return redirect(url_for('twitter.login'))

    # Get the response from github and get the necessary user info
    resp = twitter.get('account/settings.json')
    assert resp.ok
    return str(resp.json())
    social_id = str(resp.json()['woeid'])
    nickname = str(resp.json()['screen_name'])

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
        login_user(new_user)
        return redirect(url_for('.user', nickname=g.user.nickname))
    else:
        login_user(user_query)
        return redirect(url_for('.user', nickname=g.user.nickname))


@mod.route('/logout')
def logout():
    '''Simply logout the user and go back to index page.
    '''
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))


@mod.route('/user/<nickname>')
@login_required
def user(nickname):
    '''Display user profile.
    '''
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()
    return render_template('users/index.html', user=user)


@mod.route('/user/<nickname>/edit', methods=['GET', 'POST'])
@login_required
def edit(nickname):
    '''User profile editing.
    '''
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()
    form = EditForm()
    all_fields = form.data.keys()
    all_fields.remove('verify_password')
    all_fields.remove('current_password')
    fields = ['password' if x=='new_password' else x for x in all_fields]
    if form.validate_on_submit():
        for field in fields:
            print field
        flash('Changes submitted successfully', 'success')
        return redirect(url_for('.edit', nickname=nickname))
    else:
        # Set default form field values based on current values in the 
        # database for user being edited.
        for field in fields:
            if field is 'password':
                pass
            else:
                setattr(getattr(form, field), 'default', getattr(user, field))
        form.process()
    return render_template('users/edit.html', user=user, form=form)

from flask import Blueprint, render_template, url_for, redirect, session, \
                  request, g, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import app, db, lm, bcrypt
from app.users import constants as USER
from app.users.forms import LoginForm
from app.users.models import User

mod = Blueprint('users', __name__)


@lm.user_loader
def load_user(id):
    '''Load the user. Required for using Flask login extention.'''
    return User.query.get(int(id))


@mod.before_request
def before_request():
    '''Push the current user into Flask's g global. If user is authenticated,
    updated their last login date/time.'''
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_login = datetime.utcnow()
        g.user.save()


@mod.route('/login', methods=['GET', 'POST'])
def login():
    '''Login user after checking credentials, which are their email and password.'''
    # If user is already logged in, redirect them to their profile. 
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.user', nickname=g.user.nickname))
    # Load login form, see if it's valid.
    form = LoginForm()
    if form.validate_on_submit():
        email    = form.email.data
        password = form.password.data
        remember = bool(form.remember.data)
        user_query = User.query.filter_by(email=email, 
                                          password=password).first()
        if user_query is None:
            flash('Email or Password is invalid', 'error')
        else:
            login_user(user_query, remember=remember)
            return redirect(request.args.get('next') or 
                            url_for('.user', nickname=user_query.nickname))
    # Render login form template
    return render_template('users/login.html',
                           form=form)

    
@mod.route('/logout')
def logout():
    '''Simply logout the user and go back to index page.'''
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))


@mod.route('/user/<nickname>')
@login_required
def user(nickname):
    '''Display user profile.'''
    #: User currently viewing the page
    current_user = g.user
    #: User who is being viewed
    user = User.query.filter_by(nickname=nickname).first()
    # Render the user profile template
    return render_template('users/index.html', user=user)

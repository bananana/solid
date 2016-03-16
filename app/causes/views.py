from flask import Blueprint, render_template, url_for, redirect, session,  \
                  request, g, flash, abort
from datetime import datetime
from app import app, db
from app.causes.models import Cause, Action
from app.users.models import User

mod = Blueprint('causes', __name__)

@mod.route('/cause/')
def index():
    causes = Cause.query.all()

    if len(causes) == 0:
        flash('No causes found', 'error')
        return redirect(url_for('index'))
    elif len(causes) == 1:
        return redirect(url_for('.dashboard', slug=causes[0].title))

    return render_template('causes/list.html', causes=causes)

@mod.route('/cause/<slug>')
@mod.route('/cause/<slug>/dashboard')
def dashboard(slug):
    #: Campaign being viewed
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    # Render campaign template
    return render_template('causes/cause.html', cause=cause)

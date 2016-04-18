from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, url_for, redirect, session,  \
                  request, g, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, db
from app.users.models import User

from .models import Cause, Action
from .forms import CauseForm, ActionForm


mod = Blueprint('causes', __name__)


def cause_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        causes = Cause.query.all()

        if len(causes) == 0:
            flash('No causes found', 'error')
            return redirect(url_for('causes.create'))

        return f(*args, **kwargs)
    return decorated_function


def multi_cause(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        causes = Cause.query.all()

        if len(causes) < 2:
            return redirect(url_for('causes.cause_detail', slug=causes[0].title))

        return f(*args, **kwargs)
    return decorated_function


@mod.route('/cause/')
@cause_required
@multi_cause
def index():
    return render_template('causes/list.html', causes=causes)


@mod.route('/cause/<slug>')
@mod.route('/cause/<slug>/dashboard')
@cause_required
def cause_detail(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    context = {
        "cause": cause,
    }

    try:
        context["creator"] = cause.creators.filter_by(id=current_user.id).count() > 0
    except AttributeError:
        context["creator"] = False

    try:
        context["supporter"] = cause.supporters.filter_by(id=current_user.id).count() > 0
    except AttributeError:
        context["supporter"] = False

    return render_template('causes/cause.html', **context)


@mod.route('/cause/add', methods=('GET', 'POST'))
@login_required
def cause_add():
    form = CauseForm(request.form)

    cause = Cause.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(cause)
        cause.creators.append(current_user)
        cause.save()
        flash('Cause created!', 'success')
        return redirect(url_for('.cause_detail', slug=cause.slug))

    context = {
        "form": form,
    }

    return render_template('causes/cause_form.html', **context)


@mod.route('/cause/<slug>/edit', methods=('GET', 'POST'))
@login_required
@cause_required
def cause_edit(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    form = CauseForm(request.form, cause)

    if form.validate_on_submit():
        form.populate_obj(cause)
        cause.update()
        flash('Cause updated!', 'success')
        return redirect(url_for('.cause_detail', slug=slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('causes/cause_form.html', **context)


@mod.route('/cause/<slug>/support')
@login_required
@cause_required
def cause_support(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause.supporters.filter_by(id=current_user.id).count() == 0:
        cause.supporters.append(current_user)
        db.session.commit()
        flash('Thanks for supporting this cause!')

    return redirect(url_for('.cause_detail', slug=slug))


@mod.route('/cause/<slug>/actions/add', methods=('GET', 'POST'))
@login_required
@cause_required
def action_add(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    form = ActionForm(request.form)

    action = Action.create(commit=False)

    if form.validate_on_submit():
        form.populate_obj(action)
        action.cause = cause
        from pdb import set_trace; set_trace() 
        action.save()
        flash('Action added!', 'success')
        return redirect(url_for('.cause_detail', slug=slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('causes/action_form.html', **context)


@mod.route('/cause/<slug>/actions/<pk>/edit', methods=('GET', 'POST'))
@login_required
@cause_required
def action_edit(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()

    action = cause.actions.filter_by(id=pk).first()

    if cause is None or action is None:
        abort(404)

    form = ActionForm(request.form, action)

    if form.validate_on_submit():
        form.populate_obj(action)
        action.update()
        flash('Action updated!', 'success')
        return redirect(url_for('.action_detail', slug=slug))

    context = {
        "cause": cause,
        "form": form,
    }

    return render_template('causes/action_form.html', **context)


@mod.route('/cause/<slug>/actions/<pk>/support', methods=('GET', 'POST'))
@login_required
@cause_required
def action_support(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()

    action = cause.actions.filter_by(id=pk).first()

    if action.supporters.filter_by(id=current_user.id).count() == 0:
        action.supporters.append(current_user)
        db.session.commit()
        flash('Thanks for supporting this action!')

    return redirect(url_for('.cause_detail', slug=slug))

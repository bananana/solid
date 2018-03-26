from datetime import datetime
from functools import wraps

from flask import (Blueprint, render_template, url_for, redirect, session,
                   request, flash, abort, Markup)
from flask_login import current_user, login_required
from flask_babel import gettext as _

from app import app, db, uploaded_images
from app.log.models import LogEvent, LogEventType
from app.posts.forms import PostForm

from .models import Cause, CauseTranslation, Action, ActionTranslation
from .forms import (CauseForm, CauseTranslationForm, ActionForm,
                    ActionTranslationForm)

from ..email import send_email


mod = Blueprint('causes', __name__)


def cause_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        causes = Cause.query.all()

        if len(causes) == 0:
            flash('No causes found', 'error')
            return redirect(url_for('causes.cause_add'))

        return f(*args, **kwargs)
    return decorated_function


@mod.route('/cause/')
@cause_required
def index():
    if session.get('last_cause', None) is not None:
        cause = Cause.query.get(session['last_cause'])
    else:
        cause = Cause.query.all()[0]
    return redirect(url_for('causes.cause_detail', slug=cause.slug))


@mod.route('/cause/<slug>')
@mod.route('/cause/<slug>/dashboard')
@cause_required
def cause_detail(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    session["last_cause"] = cause.id

    page = request.args.get('page', 1, type=int)

    log = LogEvent.query.filter(
        (
            (LogEvent.item == cause) | (
                (LogEvent.item_type == 'Action')
                & (LogEvent.item_id.in_([a.id for a in cause.actions.all()]))
            ) | (
                (LogEvent.item_type == 'Post')
                & (LogEvent.item_id.in_([p.id for p in cause.posts.all()]))
            )
        ) & (LogEvent.item_id != LogEventType.EVENT_TYPES['cause_edit'])
    ).order_by(LogEvent.logged_at.desc()).paginate(
        page, app.config['LOG_PER_PAGE'], False
    )

    context = {
        "cause": cause,
        "log": log,
        "actions": cause.actions.filter(
            (Action.expiration >= datetime.now()) |
            (Action.expiration == None)
        ),
        "post_form": PostForm()
    }

    try:
        context["creator"] = cause.creators.filter_by(id=current_user.id).count() > 0
    except AttributeError:
        context["creator"] = False

    try:
        context["supporter"] = cause.supporters.filter_by(id=current_user.id).count() > 0
    except AttributeError:
        context["supporter"] = False

    context["cause_support"] = session.pop("cause_support", None)

    return render_template('causes/cause.html', **context)


@mod.route('/cause/add', methods=('GET', 'POST'))
@mod.route('/cause/<slug>/edit', methods=('GET', 'POST'))
@login_required
def cause_add_edit(slug=None):
    if slug is None:
        form = CauseForm(request.form)
        form_trans = CauseTranslationForm(request.form)

        cause = Cause.create(commit=False)
        cause_translation = CauseTranslation()

        if not current_user.is_admin:
            abort(404)
    else:
        cause = Cause.query.filter_by(slug=slug).first()

        if cause is None:
            abort(404)

        form = CauseForm(request.form, obj=cause)
        form_trans = CauseTranslationForm(request.form, obj=cause)

        if current_user not in cause.creators.all() and not current_user.is_admin:
            abort(404)

    if form.validate_on_submit() and form_trans.validate_on_submit():
        form.populate_obj(cause)

        if request.files['image'].filename:
            filename = uploaded_images.save(request.files['image'])
            cause.image = filename

        if slug is None:
            form_trans.populate_obj(cause_translation)

            cause.fallback_translation = cause_translation
            cause.creators.append(current_user)
            cause.save()

            flash(_('Cause created!'), 'success')
            LogEvent._log('cause_add', cause, user=current_user)
        else:
            form_trans.populate_obj(cause)
            
            cause.update()
            flash('Cause updated!', 'success')
            LogEvent._log('cause_edit', cause, user=current_user)

        return redirect(url_for('.cause_detail', slug=cause.slug))

    context = {
        "cause": cause,
        "form": form,
        "form_trans": form_trans
    }

    return render_template('causes/cause_form.html', **context)


@mod.route('/cause/<slug>/support')
@login_required
@cause_required
def cause_support(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    if current_user not in cause.supporters.all():
        cause.supporters.append(current_user)
        db.session.commit()
        send_email('Thanks for supporting "{0.title}"'.format(cause),
                   [current_user.email,],
                   {'user': current_user, 'cause': cause},
                   'email/cause_support_supporter.txt')
        send_email('New supporter for "{0.title}"'.format(cause),
                   [s.email for s in cause.creators.all()],
                   {'user': current_user, 'cause': cause},
                   'email/cause_support_creators.txt')
        flash(Markup('Thanks for supporting this cause! <a href="#actions">Take action</a> to see it succeed.'), 'success')
        LogEvent._log('cause_support', cause, user=current_user)
        session['cause_support'] = cause.slug
    else:
        flash('You are already supporting this cause.', 'error')

    return redirect(url_for('.cause_detail', slug=slug))


@mod.route('/cause/<slug>/creators')
@login_required
@cause_required
def view_cause_creators(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    context = {
        "cause": cause,
        "user": current_user,
    }

    if current_user in cause.supporters.all():
        return render_template('causes/creators.html', **context)
    else:
        abort(404)


@mod.route('/cause/<slug>/supporters')
@login_required
@cause_required
def view_cause_supporters(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    context = {
        "cause": cause,
    }

    if current_user in cause.supporters.all():
        return render_template('causes/supporters.html', **context)
    else:
        abort(404)


@mod.route('/cause/<slug>/actions')
@cause_required
def view_cause_actions(slug):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    context = {
        "cause": cause,
        "actions": cause.actions
    }
    
    return render_template('causes/actions.html', **context)


@mod.route('/cause/<slug>/actions/<pk>')
@cause_required
def view_single_action(slug, pk=None):
    cause = Cause.query.filter_by(slug=slug).first()
    
    if cause is None:
        abort(404)

    action = cause.actions.filter_by(id=pk).first()

    if action is None:
        abort(404)

    context = {
        "cause": cause,
        "action": action
    }

    if current_user in action.supporters.all():
        flash(Markup('You are supporting this action! <a href="/cause/' + 
                     cause.slug + '/actions">See other ways you can help ' + 
                     cause.title + '</a>.'), 'success')

    return render_template('causes/action_single.html', **context)


@mod.route('/cause/<slug>/actions/add', methods=('GET', 'POST'))
@mod.route('/cause/<slug>/actions/<pk>/edit', methods=('GET', 'POST'))
@login_required
@cause_required
def action_add_edit(slug, pk=None):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)
    
    if current_user not in cause.creators.all() and not current_user.is_admin:
        abort(404)

    if pk is None:
        form = ActionForm(request.form)
        form_trans = ActionTranslationForm(request.form)

        action = Action.create(commit=False)
        action_translation = ActionTranslation()
    else:
        action = cause.actions.filter_by(id=pk).first()

        form = ActionForm(request.form, obj=action)
        form_trans = ActionTranslationForm(request.form, obj=action)

        if action is None:
            abort(404)

    if form.validate_on_submit() and form_trans.validate_on_submit():
        form.populate_obj(action)

        if request.files['image'].filename:
            filename = uploaded_images.save(request.files['image'])
            action.image = filename

        if pk is None:
            form_trans.populate_obj(action_translation)

            action.fallback_translation = action_translation

            action.cause = cause
            action.save()

            send_email(u'Cause Update: A New Action is Available for {0.title}"'.format(cause),
                       [u.email for u in cause.supporters.all()],
                       {'cause': cause, 'action': action},
                       'email/cause_action_supporter.txt')
            flash('Action added!', 'success')
            LogEvent._log('action_add', action, user=current_user)
        else:
            form_trans.populate_obj(action)

            action.update()
            flash('Action updated!', 'success')

        return redirect(url_for('.cause_detail', slug=slug))

    context = {
        "cause": cause,
        "action": action,
        "form": form,
        "form_trans": form_trans
    }

    return render_template('causes/action_form.html', **context)


@mod.route('/cause/<slug>/actions/<pk>/delete')
@login_required
@cause_required
def action_delete(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None or pk is None:
        abort(404)

    action = cause.actions.filter_by(id=pk).first()

    if action is None:
        abort(404)

    if current_user in cause.creators.all() or current_user.is_admin:
        action.delete()
        flash('Action deleted successfully', 'success')

    return redirect(url_for('.cause_detail', slug=slug))


@mod.route('/cause/<slug>/actions/<pk>/support', methods=('GET', 'POST'))
@login_required
@cause_required
def action_support(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    action = cause.actions.filter_by(id=pk).first()

    if action is None:
        abort(404)

    if current_user not in action.supporters.all():
        cause.supporters.append(current_user)
        action.supporters.append(current_user)
        db.session.commit()
        send_email('Thanks for taking action!',
                   [current_user.email,],
                   {'user': current_user, 'cause': cause, 'action': action},
                   'email/action_support_supporter.txt')
        LogEvent._log('action_support', action, user=current_user)

    #return ('', 204)
    return redirect(url_for('.view_single_action', slug=slug, pk=pk)) 


@mod.route('/cause/<slug>/actions/<pk>/thanks')
@cause_required
def action_thanks(slug, pk):
    cause = Cause.query.filter_by(slug=slug).first()

    if cause is None:
        abort(404)

    action = cause.actions.filter_by(id=pk).first()

    if action is None:
        abort(404)

    context = {
        "user": current_user,
        "cause": cause,
        "action": action,
    }

    return render_template('causes/action_thanks.html', **context)

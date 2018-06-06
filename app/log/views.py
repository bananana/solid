from flask import (Blueprint, render_template, url_for, redirect, request,
                   flash, abort)
from flask_login import current_user, login_required
from app import app, db
from .models import *
from app.users.models import User

mod = Blueprint('log', __name__)


@mod.route('/log/<log_item_id>/user/<user_id>/like', methods=('GET', 'POST'))
@login_required
def like(log_item_id, user_id):
    log_item = LogEvent.query.filter_by(id=log_item_id).first()
    user = User.query.filter_by(id=user_id).first()

    # Prevent users from liking on behalf of others
    if user.id is current_user.id:
        log_item.likers.append(current_user)
        db.session.commit()
        return('', 204)
    else:
        abort(404)

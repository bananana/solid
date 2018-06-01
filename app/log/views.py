from flask import (Blueprint, render_template, url_for, redirect, request,
                   flash, abort)
from flask_login import current_user, login_required
from .models import *
from app import db

mod = Blueprint('log', __name__)


@mod.route('/log/<log_item_id>/user/<user_id>/like', methods=('GET', 'POST'))
@login_required
def like(log_item_id, user_id):
    log_item = LogEvent.query.filter_by(id=log_item_id).first()
    user = User.query.filter_by(id=user_id).first()

    # Prevent users from liking on behalf of others
    if user.id is current_user.id:
        
    else:
        abort(404)



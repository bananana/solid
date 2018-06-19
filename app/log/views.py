from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user

from app import app 

mod = Blueprint('log', __name__)

from .models import *


@mod.route('/notifications/unread')
@login_required
def notifications_list_unread():
    user = current_user

    page = request.args.get('page', 1, type=int)

    log = user.notifications().paginate(page, app.config['LOG_PER_PAGE'], False)

    context = {
        "log": log,
    }
    
    return render_template('log/notifications.html', **context)

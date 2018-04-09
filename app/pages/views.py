from flask import (Blueprint, render_template, url_for, redirect, request, g,
                   flash, abort)

from sqlalchemy.orm.exc import NoResultFound

from app.pages.models import Page


mod = Blueprint('pages', __name__)


@mod.route('/<url>')
def page_detail(url):
    try:
        page = Page.query.filter_by(url='/{0}'.format(url)).one()
    except NoResultFound:
        abort(404)

    return render_template('pages/page.html', page=page)

from flask import Blueprint, render_template, url_for, redirect, session, \
                  request, g, flash, abort


from app.pages.models import Page


mod = Blueprint('pages', __name__)


@mod.route('/<url>')
def page_detail(url):
    page = Page.query.filter_by(url='/{0}'.format(url)).one()

    return render_template('pages/page.html', page=page)

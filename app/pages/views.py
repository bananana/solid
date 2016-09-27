from flask import Blueprint, render_template, url_for, redirect, session, \
                  request, g, flash, abort

mod = Blueprint('pages', __name__)

from app.pages.models import Page


def page_detail(url):
    page = Page.query.filter_by(url=url).first()

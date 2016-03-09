from flask import Blueprint, render_template, url_for
from app import app

mod = Blueprint('styleguide', __name__)


@mod.route('/styleguide')
@mod.route('/styleguide/about')
def styleguide():
    return render_template('styleguide/index.html')

@mod.route('/styleguide/grid_system')
def grid_system():
    return render_template('styleguide/grid_system.html')

@mod.route('/styleguide/typography')
def typography():
    return render_template('styleguide/typography.html')

@mod.route('/styleguide/forms')
def forms():
    return render_template('styleguide/forms.html')

@mod.route('/styleguide/tables')
def tables():
    return render_template('styleguide/tables.html')

@mod.route('/styleguide/alerts')
def alerts():
    return render_template('styleguide/alerts.html')

@mod.route('/styleguide/utilities')
def utilities():
    return render_template('styleguide/utilities.html')

@mod.route('/styleguide/media_queries')
def media_queries():
    return render_template('styleguide/media_queries.html')

@mod.route('/styleguide/templating')
def templating():
    return render_template('styleguide/templating.html')

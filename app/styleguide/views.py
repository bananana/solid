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

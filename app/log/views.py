from flask import (Blueprint, render_template, url_for, redirect, request,
                   flash, abort)

mod = Blueprint('log', __name__)

from .models import *

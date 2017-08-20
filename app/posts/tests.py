from flask import url_for
from flask_login import current_user

from app.tests_base import BaseTestCase
from app.users.models import User
from app.causes.models import Cause
from app import app


class PostsViewsTests(BaseTestCase):
    #: Enable testing mode
    app.config['TESTING'] = True

    #: Do not render templates, we're only testing logic here.
    render_templates = False

    def test_post_create(self):
        pass

from flask import url_for
from flask_login import current_user

from app.tests_base import BaseTestCase
from app.users.models import User
from app.causes.models import Cause
from app import app


class CauseViewsTests(BaseTestCase):
    #: Enable testing mode
    app.config['TESTING'] = True

    #: Do not render templates, we're only testing logic here.
    render_templates = False

    def test_cause_create(self):
        pass

    def test_cause_create_fail(self):
        pass

    def test_user_cause_support(self):
        u = User.create(**self.test_user)
        c = Cause.create(**self.test_cause)
        u.support(c)
        self.assertTrue(u.is_supporting(c))

    def test_user_cause_unsupport(self):
        u = User.create(**self.test_user)
        c = Cause.create(**self.test_cause)
        u.support(c)
        u.unsupport(c) 
        self.assertFalse(u.is_supporting(c))

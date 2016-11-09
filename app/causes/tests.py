from flask import url_for
from flask_login import current_user, login_user, logout_user

from app.tests_base import BaseTestCase
from app.users.models import User
from app.causes.models import Cause
from app import app


class UserViewsTests(BaseTestCase):

    #: Enable testing mode
    app.config['TESTING'] = True

    #: Do not render templates, we're only testing logic here.
    render_templates = False

    #: Dummy user profiles
    test_user = {
        'nickname'  : 'Tester',
        'full_name' : 'Test Testov',
        'email'     : 'test@test.com',
        'phone'     : 1234567890,
        'zip'       : 12345,
        'employer'  : 'Boss'
    }
    test_user_2 = {
        'nickname'  : 'Tester2',
        'full_name' : 'Test Testova',
        'email'     : 'test2@test.com',
        'phone'     : 9876543210,
        'zip'       : 54321,
        'employer'  : 'Moss'
    }

    #: Dummy admin profile
    test_admin = {
        'nickname'  : 'Buster',
        'full_name' : 'Ban Hammer',
        'email'     : 'test@admin.com',
        'is_admin'  : True
    }

    #: Dummy cause
    test_cause = { 
        'title'     : 'Test Cause',
        'slug'      : 'test_cause',
        'boss'      : 'Boss'
    }

    def test_cause_create(self):
        a = User.create(**self.test_admin)
        with self.client:
            login_user(a)
            return self.client.get(url_for('users.delete', nickname=u.nickname))

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

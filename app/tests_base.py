import os

from app import app, db
from app.config.base import basedir

from flask_testing import TestCase
from flask_login import current_user, login_user, logout_user

class BaseTestCase(TestCase):
    #: Dummy user profiles
    test_user = {
        'nickname'  : 'Tester',
        'full_name' : 'Test Testov',
        'email'     : 'test@test.com',
        'phone'     : 1234567890,
        'zip'       : '12345',
        'employer'  : 'Boss'
    }
    test_user_2 = {
        'nickname'  : 'Tester2',
        'full_name' : 'Test2 Testov',
        'email'     : 'test2@test.com',
        'phone'     : 9876543210,
        'zip'       : '54321',
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

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['SERVER_NAME'] = 'localhost'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _login(self, user):
        login_user(user)
        with self.client.session_transaction() as session:
            session['user_id'] = user.id
            session['_fresh'] = True # https://flask-login.readthedocs.org/en/latest/#fresh-logins

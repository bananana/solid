import os
from flask.ext.testing import TestCase
from app import app, db
from app.config.base import basedir

class BaseTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    '''
    def login(self, email, password):
        return self.app.post('/login', data=dict(
            email=email,
            password=password,
            remember='n'
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    '''

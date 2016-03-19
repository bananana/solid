from app import app, bcrypt
from app.tests_base import BaseTestCase
from app.users.models import User
from flask.ext.login import current_user

class UserViewsTests(BaseTestCase):

    #: Dummy user profile to be recycled by tests
    test_user = {
        'nickname' : 'Tester',
        'password' : bcrypt.generate_password_hash('test'),
        'full_name' : 'Test Testov',
        'email' : 'test@test.com',
        'phone' : 1234567890,
        'zip' : 12345,
        'employer' : 'Boss'
    }

    def signup(self, context, email, nickname, password, verify_password):
        return context.post('/signup', data={
            'email' : email,
            'nickname' : nickname,
            'password' : password,
            'verify_password' : verify_password
        }, follow_redirects=True)

    def login(self, context, email, password):
        return context.post('/login', data={
            'email' : email,
            'password' : password,
            'remember' : 'n'
        }, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_user_signup(self):
        with app.test_client() as c:
            self.signup(c, 'test.signup@test.com', 'SignupTest', 'test', 'test')
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.logout()

    def test_user_login(self):
        User.create(**self.test_user)
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Tester')
            self.assertEqual(current_user.email, 'test@test.com')
            self.logout()

    def test_user_logout(self):
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            self.logout()
            # For some reason assertIsNone() doesn't work
            self.assertEqual(current_user, None)

    def test_user_initials_generation(self):
        User.create(**self.test_user)
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            current_user.generate_initials()
            self.assertTrue(current_user.initials, 'IT')

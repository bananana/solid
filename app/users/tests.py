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
    
    def edit(self, context, nickname, fields):
        return context.post('/user/' + nickname + '/edit', data=fields)

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

    def test_user_logout(self):
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            self.logout()
            # For some reason assertIsNone() doesn't work
            self.assertEqual(current_user, None)

    def test_user_delete(self):
        User.create(**self.test_user)
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            return c.get('/user/' + current_user.nickname + '/delete')
            user = User.querty.filter_by(nickname='Tester').first()
            self.assertEqual(user, None)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            
    def test_user_edit(self):
        User.create(**self.test_user)
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            self.edit(c, 'Tester', fields={
                'nickname':'Tester2',
                'full_name':'Different Name',
                'email':'different.email@test.com',
                'phone':9876543210,
                'zip':54321,
                'employer':'Another Employer',
                'description':'Test description'
            })
            self.assertEqual(current_user.nickname, 'Tester2')
            self.assertEqual(current_user.full_name, 'Different Name')
            self.assertEqual(current_user.email, 'different.email@test.com')
            self.assertEqual(current_user.phone, 9876543210)
            self.assertEqual(current_user.zip, 54321)
            self.assertEqual(current_user.employer, 'Another Employer')
            self.assertEqual(current_user.description, 'Test description')

    def test_user_initials_generation(self):
        User.create(**self.test_user)
        with app.test_client() as c:
            self.login(c, 'test@test.com', 'test')
            current_user.generate_initials()
            self.assertTrue(current_user.initials, 'IT')

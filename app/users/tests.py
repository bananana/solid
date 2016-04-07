from flask import url_for
from flask.ext.login import current_user, login_user, logout_user
from app.tests_base import BaseTestCase
from app.users.models import User

class UserViewsTests(BaseTestCase):
    
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

    #: Dummpy cause
    test_cause = { 
        'title'     : 'Test Cause',
        'slug'      : 'test_cause',
        'boss'      : 'Boss'
    }

    def test_user_signup(self):
        with self.client: 
            response = self.client.post(url_for('users.signup'), data={
                'email'           : 'test@test.com',
                'nickname'        : 'Tester',
                'password'        : 'test',
                'verify_password' : 'test' 
            })
            self.assert_redirects(response, 
                                  url_for('users.user', nickname='Tester'))
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Tester')
            self.assertEqual(current_user.email, 'test@test.com')

    def test_user_signup_fail(self):
        with self.client: 
            response = self.client.post(url_for('users.signup'), data={
                'email'           : 'test@test.com',
                'nickname'        : 'Tester',
                'password'        : 'test',
                'verify_password' : 'tset' 
            })
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assert_200(response)

    def test_user_login(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'email'    : 'test@test.com',
                'password' : 'test',
                'remember' : 'n'
            })
            self.assert_redirects(response, 
                                  url_for('users.user', nickname='Tester'))
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Tester')
            self.assertEqual(current_user.email, 'test@test.com')

    def test_user_login_fail(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'email'    : 'test@test.com',
                'password' : 'password',
                'remember' : 'n'
            })
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assert_200(response)

    def test_user_logout(self):
        u = User.create(**self.test_user)
        with self.client:
            login_user(u)
            response = self.client.get(url_for('users.logout'))
            self.assert_redirects(response, url_for('index'))
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)

    def test_user_delete(self):
        u = User.create(**self.test_user)
        with self.client: 
            login_user(u) 
            return self.client.get(url_for('users.delete', nickname=current_user.nickname))
            q = User.query.filter_by(nickname='Tester').first()
            self.assertIsNone(q)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)

    def test_user_delete_by_admin(self):
        u = User.create(**self.test_user)
        a = User.create(**self.test_admin)
        with self.client:
            login_user(a)
            return self.client.get(url_for('users.delete', nickname=u.nickname))
            q = User.query.filter_by(nickname='Tester').first()
            self.assertIsNone(q)
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Buster')

    def test_user_delete_fail(self):
       u = User.create(**self.test_user)
       u2 = User.create(**self.test_user_2)
       with self.client:
           login_user(u)
           response = self.client.get(url_for('users.delete', 
                                              nickname=u2.nickname),
                                      follow_redirects=True)
           q = User.query.filter_by(nickname='Tester').first()
           self.assertIsNotNone(q)


'''
from app import bcrypt
from app.tests_base import BaseTestCase
from app.users.models import User
from app.causes.models import Cause
from flask.ext.login import current_user
#from flask import url_for

class UserViewsTests(BaseTestCase):
    #: Dummy user profile to be recycled by tests
    test_user = {
        'nickname'  : 'Tester',
        'password'  : bcrypt.generate_password_hash('test'),
        'full_name' : 'Test Testov',
        'email'     : 'test@test.com',
        'phone'     : 1234567890,
        'zip'       : 12345,
        'employer'  : 'Boss'
    }

    #: Dummpy cause to be recycled by tests
    test_cause = { 
        'title'     : 'Test Cause',
        'slug'      : 'test_cause',
        'boss'      : 'Boss'
    }

    def signup(self, context, email, nickname, password, verify_password):
        return context.post('/signup', data={
            'email'           : email,
            'nickname'        : nickname,
            'password'        : password,
            'verify_password' : verify_password
        }, follow_redirects=True)

    def login(self, context, email, password):
        return context.post('/login', data={
            'email'    : email,
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
                'nickname'    : 'Tester2',
                'full_name'   : 'Different Name',
                'email'       : 'different.email@test.com',
                'phone'       : 9876543210,
                'zip'         : 54321,
                'employer'    : 'Another Employer',
                'description' : 'Test description'
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

    def test_user_cause_support(self):
        user = User.create(**self.test_user)
        cause = Cause.create(**self.test_cause)
        user.support(cause)
        self.assertTrue(user.is_supporting(cause))

    def test_user_cause_unsupport(self):
        user = User.create(**self.test_user)
        cause = Cause.create(**self.test_cause)
        user.support(cause)
        user.unsupport(cause) 
        self.assertFalse(user.is_supporting(cause))
'''

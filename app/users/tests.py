from flask import url_for
from flask_login import current_user

from app.tests_base import BaseTestCase
from app.users.models import User
from app.causes.models import Cause
from app import app

class UserViewsTests(BaseTestCase):
    #: Enable testing mode
    app.config['TESTING'] = True

    #: Do not render templates, we're only testing logic here.
    render_templates = True

    def test_user_signup(self):
        with self.client: 
            response = self.client.post(url_for('users.signup'), data={
                'email'           : 'test@test.com',
                'nickname'        : 'Tester',
                'password'        : 'test',
                'verify_password' : 'test' 
            })
            self.assert_redirects(response, 
                                  url_for('index'))
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Tester')
            self.assertEqual(current_user.email, 'test@test.com')

    def test_user_signup_invalid(self):
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

    def test_user_signup_duplicate_username(self):
        u = User.create(**self.test_user)
        with self.client: 
            response = self.client.post(url_for('users.signup'), data={
                'email'           : 'test2@test.com',
                'nickname'        : 'Tester',
                'password'        : 'test',
                'verify_password' : 'test' 
            })
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assert_200(response)

    def test_user_signup_authenticated_redirects(self):
        u = User.create(**self.test_user)
        with self.client:
            self._login(u)
            response = self.client.get(url_for('users.signup'))

            self.assert_redirects(response, url_for('users.user',
                                  nickname=u.nickname))

    def test_user_login_email(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'login'    : 'test@test.com',
                'password' : 'test',
                'remember' : 'n'
            })

            self.assert_redirects(response, 
                                  url_for('index'))
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(current_user.nickname, 'Tester')

    def test_user_login_nickname(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'login'    : 'Tester',
                'password' : 'test',
                'remember' : 'n'
            })

            self.assert_redirects(response, 
                                  url_for('index'))
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(current_user.nickname, 'Tester')

    def test_user_login_double_redirects(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            data = {
                'login'    : 'test@test.com',
                'password' : 'test',
                'remember' : 'n'
            }
            response = self.client.post(url_for('users.login'), data=data)

            self.assert_redirects(response, 
                                  url_for('index'))
            self.assertTrue(current_user.is_authenticated)

            response = self.client.post(url_for('users.login'), data=data)

            self.assert_redirects(response, 
                                  url_for('index'))
            self.assertTrue(current_user.is_authenticated)

    def test_user_login_fail(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'login'    : 'test@test.com',
                'password' : 'incorrect',
                'remember' : 'n'
            })
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assert_200(response)

    def test_user_login_fail_invalid(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        with self.client:
            response = self.client.post(url_for('users.login'), data={
                'login'    : 'test@test.com',
            })
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)
            self.assert_200(response)

    def test_user_logout(self):
        u = User.create(**self.test_user)
        with self.client:
            self._login(u)
            self.assertTrue(current_user.is_authenticated)
            response = self.client.get(url_for('users.logout'))
            self.assert_redirects(response, url_for('index'))
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)

    def test_user_delete(self):
        u = User.create(**self.test_user)
        with self.client: 
            self._login(u)
            self.client.get(url_for('users.delete', nickname=current_user.nickname))
            q = User.query.filter_by(nickname='Tester').first()
            self.assertIsNone(q)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(current_user.is_anonymous)

    def test_user_delete_by_admin(self):
        u = User.create(**self.test_user)
        a = User.create(**self.test_admin)
        with self.client as client:
            self._login(a)

            client.get(url_for('users.delete', nickname=u.nickname))

            q = User.query.filter_by(nickname=self.test_user['nickname']).first()
            self.assertIsNone(q)
            self.assertTrue(current_user.is_authenticated)
            self.assertFalse(current_user.is_anonymous)
            self.assertEqual(current_user.nickname, 'Buster')

    def test_user_delete_fail_permission(self):
       u = User.create(**self.test_user)
       u2 = User.create(**self.test_user_2)
       with self.client:
           self._login(u)
           response = self.client.get(url_for('users.delete', 
                                              nickname=u2.nickname),
                                      follow_redirects=True)
           self.assert_403(response)
           q = User.query.filter_by(nickname=self.test_user['nickname']).first()
           self.assertIsNotNone(q)

    def test_user_delete_fail_notfound(self):
       u = User.create(**self.test_user)
       with self.client:
           self._login(u)
           response = self.client.get(url_for('users.delete', 
                                              nickname='nonexistent'))
           self.assert_404(response)
           q = User.query.filter_by(nickname=self.test_user['nickname']).first()
           self.assertIsNotNone(q)

    def test_user_edit(self):
        u = User.create(**self.test_user)
        with self.client as client: 
            self._login(u)
            data = {
                'nickname'    : 'Tester2',
                'full_name'   : 'Different Name',
                'email'       : 'different.email@test.com',
                'phone'       : 9876543210,
                'zip'         : '54321',
                'employer'    : 'Another Employer',
                'description' : 'Test description',
                'new_password'    : 'password',
                'verify_password' : 'password',
            }
            client.post(url_for('users.edit', nickname=u.nickname), data=data)
            self.assertEqual(current_user.nickname, data['nickname'])
            self.assertEqual(current_user.full_name, data['full_name'])
            self.assertEqual(current_user.email, data['email'])
            self.assertEqual(current_user.phone, data['phone'])
            self.assertEqual(current_user.zip, data['zip'])
            self.assertEqual(current_user.employer, data['employer'])
            self.assertEqual(current_user.description, data['description'])
            self.assertTrue(u.is_valid_password('password'))

    def test_user_edit_fail_invalid(self):
        u = User.create(**self.test_user)
        with self.client as client: 
            self._login(u)
            data = {
                'new_password'    : 'password',
            }
            response = client.post(url_for('users.edit', nickname=u.nickname), data=data)
            self.assert_200(response)
            self.assertGreater(self.get_context_variable('form').errors, 0)


    def test_user_edit_fail_permission(self):
        u = User.create(**self.test_user)
        u2 = User.create(**self.test_user_2)
        with self.client: 
            self._login(u)
            response = self.client.post(
                url_for('users.edit', nickname=u2.nickname), data={
                    'nickname'    : 'Tester3',
                    'full_name'   : 'Different Name',
                    'email'       : 'different.email@test.com',
                    'phone'       : 000,
                    'zip'         : 000,
                    'employer'    : 'Another Employer'
                }
            )
            self.assert_403(response)
            self.assertEqual(u2.nickname, self.test_user_2['nickname'])
            self.assertEqual(u2.full_name, self.test_user_2['full_name'])
            self.assertEqual(u2.email, self.test_user_2['email'])
            self.assertEqual(u2.phone, self.test_user_2['phone'])
            self.assertEqual(u2.zip, self.test_user_2['zip'])
            self.assertEqual(u2.employer, self.test_user_2['employer'])

    def test_user_edit_fail_notfound(self):
        u = User.create(**self.test_user)
        with self.client: 
            self._login(u)
            response = self.client.post(
                url_for('users.edit', nickname='nonexistent'), data={
                    'nickname'    : 'Tester3',
                    'full_name'   : 'Different Name',
                    'email'       : 'different.email@test.com',
                    'phone'       : 000,
                    'zip'         : 000,
                    'employer'    : 'Another Employer'
                }
            )
            self.assert_404(response)
            self.assertEqual(u.nickname, self.test_user['nickname'])
            self.assertEqual(u.full_name, self.test_user['full_name'])
            self.assertEqual(u.email, self.test_user['email'])
            self.assertEqual(u.phone, self.test_user['phone'])
            self.assertEqual(u.zip, self.test_user['zip'])
            self.assertEqual(u.employer, self.test_user['employer'])

    def test_user_password_setting(self):
        u = User.create(**self.test_user)
        u.set_password('test')
        self.assertTrue(u.is_valid_password('test'))
        self.assertFalse(u.is_valid_password('tset'))

    def test_user_initials_generation(self):
        u = User.create(**self.test_user)
        self._login(u)
        current_user.generate_initials()
        self.assertTrue(current_user.initials, 'TT')

    def test_user_profile(self):
        u = User.create(**self.test_user)
        with self.client as client: 
            self._login(u)
            response = client.get(url_for('users.user', nickname=u.nickname))
            self.assert_context('user', u)
            self.assert_200(response)

    def test_user_profile_fail_notfound(self):
        u = User.create(**self.test_user)
        with self.client as client: 
            self._login(u)
            response = client.get(url_for('users.user', nickname='nonexistent'))
            self.assert_404(response)

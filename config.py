import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'replace-with-truly-random-string-for-production'
#SECRET_KEY = os.urandom(24)
HOST = 'localhost'
PORT = '5000'
DEBUG = True
TESTING = False

WTF_CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Move to environment variables for production
OAUTH_CREDENTIALS = {
    'github': {
        'id': '',
        'secret': '',
        'redirect': 'users.authorize_github'
    },
    'twitter': {
        'id': '',
        'secret': '',
        'redirect': 'users.authorize_twitter'
    }
}

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

'''
OAUTH_CREDENTIALS = {
    'github': {
        'id': '838a5146c0c02c49b6b1',
        'secret': '5ec8fef4e5ad9c0340e1c382f302a9fd4ab72b4b'
    },
    'twitter': {
        'id: 'MXRHGhjB19kPKLd3G0hywzqAc',
        'secret': 'Fe7ckjmAhyf1fcuhmDTxb2CAUWs9Ms66KbTwsYy5nyW4vlZf9g'
    }
}
'''

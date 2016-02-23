import os

basedir = os.path.abspath(os.path.dirname(__file__))

#SECRET_KEY = os.urandom(24)
SECRET_KEY = 'replace-with-truly-random-string-for-production'
HOST = 'localhost'
PORT = '5000'
DEBUG = True
TESTING = False

WTF_CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

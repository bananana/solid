# -*- coding: utf-8 -*-

import os

d = os.path.dirname

basedir = os.path.abspath(
	d(d(d(__file__)))
)

SECRET_KEY = 'replace-with-truly-random-string-for-production'

SITE_NAME = 'Solid'

CONTACT_EMAIL = 'solid@brandworkers.org'

DEBUG = False
TESTING = False

WTF_CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SUPPORTED_LANGUAGES = {
    'en': u'English',
    'es': u'Español'
}

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'EST'

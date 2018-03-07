# -*- coding: utf-8 -*-

import os

d = os.path.dirname

basedir = os.path.abspath(
	d(d(d(__file__)))
)

SECRET_KEY = 'replace-with-truly-random-string-for-production'

SITE_NAME = 'Solid'

CONTACT_EMAIL = 'solid@brandworkers.org'
DEFAULT_EMAIL_SENDER = 'noreply@bsolid.org'

DEBUG = False
TESTING = False

WTF_CSRF_ENABLED = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'EST'

UPLOADS_DEFAULT_DEST = os.path.join(basedir, '..', 'uploads')
RESIZE_ROOT = os.path.join(basedir, '..', 'resized')

MAILGUN_API_KEY = 'key-e57445fe7e1ad02c5481f8398186589f'
MAILGUN_DOMAIN = 'sandbox40316c4ae2364191a9387fe1be902d37.mailgun.org'

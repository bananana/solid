from app.config.base import *

DEBUG = True

SERVER_NAME = 'localhost:5000'

MAIL_PORT = 1025
MAIL_DEFAULT_SENDER = 'noreply@bsolid.org'

GOOGLE_OAUTH_CLIENT_ID = ''
GOOGLE_OAUTH_CLIENT_SECRET = ''

TWITTER_OAUTH_API_KEY = 'lJSXD0D0SFG3qHIhdRR0YaxVI'
TWITTER_OAUTH_API_SECRET = 'lSCt1Srf6zgPsH1F6av4ouNhePOYxyUhWPwf7tiaIOiMXUJ7BY'

FACEBOOK_OAUTH_CLIENT_ID = '733401776796802'
FACEBOOK_OAUTH_CLIENT_SECRET = '1a6d52a5e39ffb7e3e018a89543ae731'

MAILGUN_API_KEY = 'key-e57445fe7e1ad02c5481f8398186589f'
MAILGUN_DOMAIN = 'sandbox40316c4ae2364191a9387fe1be902d37.mailgun.org'

SECRET_KEY = 'veryverysecret'

RESIZE_URL = 'http://{0}/static/uploads/'.format(SERVER_NAME)
UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'app', 'static', 'uploads')
RESIZE_ROOT = UPLOADS_DEFAULT_DEST

SENTRY_CONFIG = {
    "dsn": '',
    "environment": "local"
}
SENTRY_JS_KEY = ''

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

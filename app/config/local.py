from app.config.base import *

DEBUG = True

SERVER_NAME = 'localhost:5000'

MAIL_PORT = 1025
MAIL_DEFAULT_SENDER = 'noreply@bsolid.org'

GOOGLE_OAUTH_CLIENT_ID = ''
GOOGLE_OAUTH_CLIENT_SECRET = ''

TWITTER_OAUTH_API_ID = ''
TWITTER_OAUTH_API_SECRET = ''

FACEBOOK_OAUTH_CLIENT_ID = ''
FACEBOOK_OAUTH_CLIENT_SECRET = ''

# Uncomment for testing purposes
#import os
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
#os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

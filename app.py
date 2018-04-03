#!venv/bin/python
#
# Name........: app.py
# Author......: Pavel Mamontov
# Version.....: 0.4
# Description.: Unified manager for Flask apps. Manipulates database, creates
#               modules, runs the app in Werkzeug, cleans up temporary files.
# License.....: GPLv3 (see LICENSE file)

from datetime import datetime, timedelta
from distutils.util import strtobool
import fnmatch
from os import path, walk, makedirs, remove
import random
from sys import argv
import unittest

if __name__ == '__main__' and len(argv) > 1 and argv[1] == 'test':
    from coverage import coverage
    cov = coverage(branch=True, include=['app/*'])
    cov.start()

from flask_script import Manager
from flask_migrate import MigrateCommand
import jinja2
from sqlalchemy import inspect
from terminaltables import AsciiTable

from app import app, db
from app.email import send_email
from app.causes.models import Cause, Action
from app.log.models import LogEvent, LogEventType
from app.posts.models import Post
from app.users.models import User


class bcolors:
    '''Unicode color codes. Borrowed from Blender build scripts.
    '''
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.option('-l', '--list', dest='list_', action='store_true')
@manager.option('-t', '--type', dest='type_', choices=['all', 'py', 'tmp'],
                default='all')
def clean(list_, type_):
    """ Clean temporary files """
    if type_ == 'all':
        file_types = ['*.*.sw?', '*~', '*.pyc', '*.stackdump']
    elif type_ == 'py':
        file_types = ['*.pyc', '*.stackdump']
    elif type_ == 'tmp':
        file_types = ['*.*.sw?', '*~']

    files = []
    for t in file_types:
        for root, dirs, _files in walk('.'):
            for f in fnmatch.filter(_files, t):
                files.append(path.join(root, f))

    if list_:
        for f in files:
            print f
    else:
        for f in files:
            remove(f)
        print(bcolors.OKGREEN + 'Removed ' + str(len(files))
              + ' files' + bcolors.ENDC)


@manager.option('-l', '--list', dest='list_', action='store_true')
@manager.option('-c', '--create', dest='name')
def mod(list_, name):
    """ List and add app modules """
    if list_:
        #: Get all directories in the app directory
        mods = walk('app').next()[1]
        # Remove static and template directories from the list
        mods.remove('static')
        mods.remove('templates')
        print('Modules present...........: ' + ', '.join(mods))
        exit(0)
    elif name:
        try:
            mod_path = 'app/' + name
            template_path = 'app/templates/' + name

            # Try to create a module and template paths. Throw exception if if any
            # of directories with same name exist.
            if not path.exists(mod_path):
                makedirs(mod_path)
            else:
                raise OSError('Module already exists')
            if not path.exists(template_path):
                makedirs(template_path)
            else:
                raise OSError('Template direcory already exists')

            # Create blank module files
            blank_mod_files = ['__init__.py','models.py','constants.py']
            for f in blank_mod_files:
                open(mod_path + '/' + f, 'w').close()

            # Create a views file and pre-fill it with blueprint declaration
            views = open(mod_path + '/views.py', 'w')
            views.write("# imports go here\n\n")
            views.write("mod = Blueprint(\'" + name + "\', __name__)\n\n")
            views.close()

            # Create a template file and prefill with some basic, empty blocks
            template = open(template_path + '/index.html', 'w')
            template.write("{% extends \"base.html\" %}\n")
            template.write("{% set active_page = \"" + name + "\" %}\n\n")
            template.write("{% block scripts %}\n")
            template.write("{% endblock %}\n\n")
            template.write("{% block content %}\n")
            template.write("{% endblock %}")
            template.close()

            # Print a message to remind user to register their module blueprint
            print('Module files are here.....: ' + mod_path)
            print('Module templates are here.: ' + template_path)
            print(bcolors.WARNING + \
                  "Don\'t forget to register your module blueprint in " + \
                  bcolors.BOLD + "app/__init__.py " + bcolors.ENDC + \
                  bcolors.WARNING + "like so:" + bcolors.ENDC)
            print('  from app.' + name + '.views import mod as ' + name + 'Module')
            print('  app.register_blueprint(' + name + 'Module)')
            print(bcolors.OKGREEN + 'Module ' + name + \
                  ' created successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)
    else:
        exit(1)


@manager.option('-c', '--create', action='store_true')
@manager.option('-d', '--delete')
@manager.option('-m', '--modify')
@manager.option('-r', '--regenerate-colors', action='store_true')
@manager.option('-l', '--list', nargs='?', dest='list_', metavar='SEARCH', const='')
def user(create, delete, modify, regenerate_colors, list_):
    # Process subcommands for user
    if create:
        u = User()

        #: Inspect user model so we can get database column types later on
        insp = inspect(User)

        #: Automatically generated keys from the User model
        #keys = sorted(u.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['nickname', 'email', 'full_name',
                'is_admin', 'password', 'social_id', 'phone', 'zip',
                'employer', 'description']

        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)
            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int): ')
                values.append(None if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool): ')
                values.append(None if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ': '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        #: Remove password from the above list because it has to be set with
        #: set_password() method
        passwd = kv.pop('password')

        # Try to create the user
        try:
            u.create(**kv)
            new_user = User.query.filter_by(nickname=kv.get('nickname')).first()
            new_user.generate_initials()
            new_user.generate_color()
            new_user.set_password(passwd)
            print(bcolors.OKGREEN + 'User ' + kv.get('nickname') + \
                  ' created successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif delete:
        try:
            to_del = User.query.filter_by(nickname=delete).first()
            to_del.delete()
            print(bcolors.OKGREEN + 'User ' + delete + \
                  ' deleted successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif modify:
        try:
            u = User.query.filter_by(nickname=modify).first()
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

        #: Inspect user model so we can get database column types later on
        insp = inspect(User)

        #: Automatically generated keys from the User model
        #keys = sorted(u.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['nickname', 'email', 'full_name',
                'is_admin', 'password', 'social_id', 'phone', 'zip',
                'employer', 'description']

        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)

            #: Get attribute that is being modified
            current_attr = getattr(u, k)

            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ' ['+ str(current_attr) + ']: '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        #: Remove password from the above list because it has to be set with
        #: set_password() method
        passwd = kv.pop('password')

        # Try to create the user
        try:
            u.update(**kv)
            u.generate_initials()
            u.set_password(passwd)
            print(bcolors.OKGREEN + 'User ' + kv.get('nickname') + \
                  ' updated successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif list_ is not None:
        insp = inspect(User)
        try:
            usr_sr = User.query.filter(User.nickname.contains(list_)).all()
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

        keys = ['id', 'nickname', 'email', 'full_name', 'is_admin']

        table_data = [keys]
        for u in usr_sr:
            usr = []
            for k in keys:
                attr = getattr(u, k)
                usr.append(('None' if attr is None else unicode(attr)))
            table_data.append(usr)
        table = AsciiTable(table_data)
        print(table.table)
        exit(0)

    elif regenerate_colors:
        for user in User.query.all():
            user.generate_color()
        print(bcolors.OKGREEN + 'Regenerated user colors' + bcolors.ENDC)
        exit(0)


@manager.option('-c', '--create', action='store_true')
@manager.option('-d', '--delete')
@manager.option('-m', '--modify')
@manager.option('-l', '--list', nargs='?', dest='list_', metavar='SEARCH', const='')
def cause(create, delete, modify, list_):
    if create:
        c = Cause()

        #: Inspect Cause model so we can get database column types later on
        insp = inspect(Cause)

        #: Automatically generated keys from the Cause model
        #keys = sorted(c.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['title', 'boss', 'location', 'video', 'image']


        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)
            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int): ')
                values.append(None if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool): ')
                values.append(None if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ': '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        # Try to create the cause
        try:
            c.create(**kv)
            print(bcolors.OKGREEN + 'Cause ' + kv.get('title') + \
                  ' created successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif delete:
        try:
            to_del = Cause.query.filter_by(slug=delete).first()
            to_del.delete()
            print(bcolors.OKGREEN + 'Cause ' + delete + \
                  ' deleted successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif modify:
        try:
            c = Cause.query.filter_by(slug=modify).first()
        except Exception as e:
            c = None
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)

        if c is None:
            print(bcolors.FAIL + 'Error: no cause found for slug "{0}"'.format(
                modify
            ) + bcolors.ENDC)
            exit(1)

        #: Inspect user model so we can get database column types later on
        insp = inspect(Cause)

        #: Automatically generated keys from the Cause model
        #keys = sorted(c.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['title', 'boss', 'location', 'video', 'image']

        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)

            #: Get attribute that is being modified
            current_attr = getattr(c, k)

            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ' ['+ str(current_attr) + ']: '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        # Try to update the cause
        try:
            c.update(**kv)
            print(bcolors.OKGREEN + 'Cause ' + kv.get('title') + \
                  ' updated successfully' + bcolors.ENDC)

            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif list_ is not None:
        try:
            cause_sr = Cause.query.filter(Cause.slug.contains(list_)).all()
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

        keys = ['id', 'title', 'slug', 'boss', 'location',
                'video', 'image']
        table_data = [keys]
        for c in cause_sr:
            cause = []
            for k in keys:
                attr = getattr(c, k)
                cause.append(('None' if attr is None else str(attr)))
            table_data.append(cause)
        table = AsciiTable(table_data)
        print(table.table)


@manager.option('-c', '--create', action='store_true')
@manager.option('-d', '--delete')
@manager.option('-m', '--modify')
@manager.option('-l', '--list', nargs='?', dest='list_', metavar='SEARCH', const='')
def action(create, delete, modify, list_):
    '''Create, delete, modify or list actions.
    '''
    if create:
        a = Action()

        #: Inspect Cause model so we can get database column types later on
        insp = inspect(Action)

        #: Automatically generated keys from the Action model
        #keys = sorted(a.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['title', 'description', 'expiration']

        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)
            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int): ')
                values.append(None if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text): ')
                values.append(None if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool): ')
                values.append(None if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ': '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        # Try to create the cause
        try:
            a.create(**kv)
            print(bcolors.OKGREEN + 'Action ' + kv.get('title') + \
                  ' created successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif delete:
        try:
            to_del = Action.query.filter_by(slug=delete).first()
            to_del.delete()
            print(bcolors.OKGREEN + 'Action ' + delete + \
                  ' deleted successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif modify:
        try:
            a = Action.query.filter_by(id=modify).first()
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

        #: Inspect user model so we can get database column types later on
        insp = inspect(Action)

        #: Automatically generated keys from the Cause model
        #keys = sorted(c.__dict__.keys()[1:])

        #: Manually created list of keys in appropriate order
        keys = ['cause_id', 'cause', 'title', 'description', 'expiration']

        #: Empty arrays to store user input
        values = []

        for k in keys:
            #: Get type of database column and cast the input into that type
            val_type = str(getattr(insp.columns, k).type)

            #: Get attribute that is being modified
            current_attr = getattr(a, k)

            if val_type == 'INTEGER':
                inpt = raw_input(k + ' (int) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else int(inpt))
            elif fnmatch.fnmatch(val_type, 'VARCHAR*'):
                inpt = raw_input(k + ' (str) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'TEXT':
                inpt = raw_input(k + ' (text) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else str(inpt))
            elif val_type == 'BOOLEAN':
                inpt = raw_input(k + ' (bool) [' + str(current_attr) + ']: ')
                values.append(current_attr if inpt == '' else strtobool(inpt))
            else:
                values.append(raw_input(k + ' ['+ str(current_attr) + ']: '))

        #: Key-value pairs to be used in the create() method of mixins.py
        kv = dict(zip(keys,values))

        # Try to update the cause
        try:
            a.update(**kv)
            print(bcolors.OKGREEN + 'Action ' + kv.get('title') + \
                  ' updated successfully' + bcolors.ENDC)
            exit(0)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    elif list_ is not None:
        try:
            action_sr = Action.query.filter(Action.title.contains(list_)).all()
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

        keys = ['cause_id', 'cause', 'title', 'description', 'expiration']
        table_data = [keys]
        for a in action_sr:
            action = []
            for k in keys:
                attr = getattr(a, k)
                action.append(('None' if attr is None else unicode(attr)))
            table_data.append(action)
        table = AsciiTable(table_data)
        print(table.table)

    else:
        print(bcolors.FAIL + 'Error: option required' + bcolors.ENDC)
        exit(1)


@manager.command
def support(nickname, cause_slug):
    '''Make user support a cause
    '''

    # Process subcommands for cause support
    try:
        user = User.query.filter_by(nickname=nickname).first()
        cause = Cause.query.filter_by(slug=cause_slug).first()
        user.support(cause)
        db.session.commit()
        print(bcolors.OKGREEN + 'User ' + nickname + \
              ' is now supporting ' + cause_slug + bcolors.ENDC)
        exit(0)
    except Exception as e:
        print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
        exit(1)


@manager.command
def unsupport(nickname, cause_slug):
    '''Make user unsupport a cause
    '''
    try:
        user = User.query.filter_by(nickname=nickname).first()
        cause = Cause.query.filter_by(slug=cause_slug).first()
        user.unsupport(cause)
        db.session.commit()
        print(bcolors.OKGREEN + 'User ' + nickname + \
              ' no longer supports ' + cause_slug + bcolors.ENDC)
    except Exception as e:
        print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
        exit(1)


@manager.command
def test(module=None, verbose=False):
    '''Run unit tests for the app.
    '''
    # If verbose flag is set, increase verbosity level to 2, otherwise leave
    # it as 1, which is default.
    verbosity = verbose and 2 or 1

    if module:
        try:
            suite = unittest.TestLoader() \
                            .loadTestsFromName('app.' + module + '.tests')
            unittest.TextTestRunner(verbosity=verbosity).run(suite)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)
    else:
        try:
            suite = unittest.TestLoader() \
                            .discover(start_dir='.', pattern='test*.py')
            unittest.TextTestRunner(verbosity=verbosity).run(suite)
        except Exception as e:
            print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
            exit(1)

    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    cov.html_report(directory='coverage')
    cov.erase()


@manager.command
def email():
    from flask import url_for

    period = (
        datetime.utcnow() - timedelta(14),
        datetime.utcnow()
    )

    for user in User.query.all():
        if user.email != 'carl@supervacuo.com':
            continue

        user_causes = user.supports

        if user_causes.count() == 0:
            continue

        user_cause_actions = Action.query.filter(Action.cause_id.in_(
            [c.id for c in user_causes.all()]
        ))

        if user_cause_actions.count() > 0:
            actions_new = [r.item for r in LogEvent.query.filter(
                (LogEvent.event_type_id == LogEventType.EVENT_TYPES['action_add'])
                & (LogEvent.logged_at > period[0])
                & (LogEvent.item_id.in_([a.id for a in user_cause_actions.all()]))
            ).all()]
            actions_supporters = [r.item for r in LogEvent.query.filter(
                (LogEvent.event_type_id == LogEventType.EVENT_TYPES['action_support'])
                & (LogEvent.logged_at > period[0])
                & (LogEvent.item_id.in_([a.id for a in user_cause_actions.all()]))
            ).all()]
        else:
            actions_new = []
            actions_supporters = []

        user_cause_posts = Post.query.filter(Post.cause_id.in_(
            [c.id for c in user_causes.all()]
        ))

        if user_cause_posts.count() > 0:
            posts_new = [r.item for r in LogEvent.query.filter(
                (LogEvent.event_type_id == LogEventType.EVENT_TYPES['post_add'])
                & (LogEvent.logged_at > period[0])
                & (LogEvent.item_id.in_([p.id for p in user_cause_posts.all()]))
            ).all()]
        else:
            posts_new = []

        causes_supporters = [r.item for r in LogEvent.query.filter(
            (LogEvent.event_type_id == LogEventType.EVENT_TYPES['cause_support'])
            & (LogEvent.logged_at > period[0])
            & (LogEvent.item_id.in_([a.id for a in user_cause_actions.all()]))
        ).all()]

        if (len(actions_new) == 0 and len(actions_supporters) == 0 and
            len(posts_new) == 0):
                continue

        highlights = actions_new + posts_new
        _highlights = []

        for highlight in random.sample(highlights, min(4, len(highlights))):
            if isinstance(highlight, Action):
                _highlights += [{
                    'url': url_for(
                        'causes.cause_detail', slug=highlight.cause.slug,
                        _external=True
                    ),
                    'title': highlight.title,
                    'type': 'action',
                    'summary': highlight.summary
                }]
            else:
                _highlights += [{
                    'url': url_for(
                        'posts.post_detail', slug=highlight.cause.slug,
                        pk=highlight.id, _external=True
                    ),
                    'title': '{0}, {1}'.format(
                        highlight.author.initials.upper(),
                        highlight.created_on.strftime('%b. %d, %Y')
                    ),
                    'type': 'post',
                    'summary': jinja2.filters.do_truncate(
                        None, highlight.body, 180, True, leeway=5
                    )
                }]

        context = {
            'user': user, 'period': period,
            'actions_new': actions_new,
            'posts_new': posts_new,
            'actions_supporters': actions_supporters,
            'causes_supporters': causes_supporters,
            'highlights': _highlights,
        }

        with app.app_context():
            if app.debug:
                context['url_for'] = lambda url, slug, _external=False, pk=None: url
                f = open('email.html', 'w')
                f.write(jinja2.Environment(
                        loader=jinja2.FileSystemLoader('app/templates/')
                    ).get_template('email/digest.html').render(context)
                )
                f.close()

            send_email('Latest updates on your Solid causes',
                       [user.email,],
                       context,
                       'email/digest.txt', template_html='email/digest.html')


if __name__ == "__main__":
    manager.run()

#!venv/bin/python
#
# Name........: app.py
# Author......: Pavel Mamontov
# Version.....: 0.4
# Description.: Unified manager for Flask apps. Manipulates database, creates
#               modules, runs the app in Werkzeug, cleans up temporary files.
# License.....: GPLv3 (see LICENSE file)

import argparse
from distutils.util import strtobool
import fnmatch 
import imp
from os import path, walk, listdir, makedirs, remove
from sys import argv
import unittest


from sqlalchemy import inspect
from migrate.exceptions import DatabaseAlreadyControlledError
from migrate.versioning import api
from textwrap import dedent
from terminaltables import AsciiTable

from app import app, db
from app.users.models import User
from app.causes.models import Cause
from app.causes.models import Cause, Action

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


class AppManager(object):
    '''Handle command line input using argparse. All other methods are called 
    from here and all exception handling is happening here.
    '''
    def __init__(self):
        parser = argparse.ArgumentParser(
            usage=dedent('''\
            ./app.py [-h] [command]

            commands:
              db          manipluate the database
              cause       manipulate causes
              action      manipulate actions
              user        manipulate users
              clean       clean temporary and/or compiled files
              mod         create new module scaffolding 
              run         run the Flask app
              test        run unit tests
            '''))
        parser.add_argument('command', help='subcommand to run')
        args = parser.parse_args(argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command) ()

    def db(self):
        '''Database manipulation commands.
        '''
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description: 
                  manipulates the databse'''),
            usage='''./app.py db [-h] [-v] [-c] [-d NUM] [-m] [-u NUM]''')
        parser.add_argument('-v',
                            '--version',
                            action='store_true',
                            help='display database version')
        parser.add_argument('-c', 
                            '--create', 
                            action='store_true', 
                            help='create database with SQLAlchemy')
        parser.add_argument('-d', 
                            '--downgrade',
                            type=int,
                            action='store', 
                            help='downgrade database')
        parser.add_argument('-m', 
                            '--migrate', 
                            action='store_true', 
                            help='migrate database')
        parser.add_argument('-u', 
                            '--upgrade',
                            type=int,
                            action='store', 
                            help='upgrade database')
        args = parser.parse_args(argv[2:])

        # Process subcommands for db 
        with app.app_context():
            database = Database(
                app.config['SQLALCHEMY_DATABASE_URI'],
                app.config['SQLALCHEMY_MIGRATE_REPO']
            )
        if args.version:
            database.print_version()
            exit(0)

        elif args.create:
            print('Creating database...')
            try:
                database.create()
                print(bcolors.OKGREEN + 'Database created successfully' + \
                      bcolors.ENDC)
                exit(0)
            except DatabaseAlreadyControlledError:
                print(bcolors.FAIL + \
                      'Error: Database already exists for this project' + \
                      bcolors.ENDC)
                exit(1)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.downgrade:
            print('Downgrading database by ' + str(args.downgrade) + \
                  ' version(s)...')
            try:
                database.downgrade(args.downgrade)
                print(bcolors.OKGREEN + 'Database downgraded successfully' + \
                      bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.migrate:
            print('Migrating database...')
            try:
                database.migrate()
                print(bcolors.OKGREEN + 'Database migrated successfully' + \
                      bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.upgrade:
            print('Upgrading database by ' + str(args.upgrade) + ' version(s)...')
            try:
                database.upgrade(args.upgrade)
                print(bcolors.OKGREEN + 'Database upgraded successfully' + \
                      bcolors.ENDC)
                exit(0)
            except KeyError:
                print (bcolors.FAIL + 'Error: Already at most recent version' + \
                       bcolors.ENDC)
                exit(1)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        else:
            parser.print_help()
            exit(0)

    def mod(self):
        '''Module manipulation commands.
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description: 
                  create new module'''),
            usage='''./app.py mod [-h] [-l] [-c NAME]''')
        parser.add_argument('-l',
                            '--list',
                            action='store_true',
                            help='list existing modules')
        parser.add_argument('-n', 
                            '--name',
                            '-c',
                            '--create',
                            nargs='?',
                            const='new_module',
                            action='store', 
                            help='create module')
        args = parser.parse_args(argv[2:])

        # Process subcommands for mod
        module = Module()
        if args.list:
            module.print_mods()
            exit(0)

        elif args.name:
            try:
                module.create(args.name) 
                print(bcolors.OKGREEN + 'Module ' + args.name + \
                      ' created successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        else:
            parser.print_help()
            exit(0)

    def user(self):
        '''Create, delete, modify or list users. 
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  create, delete, modify or list users'''),
            usage='''./app.py create [-c] [-d USER] [-l] [-m USER] [-s USER]''')
        parser.add_argument('-c',
                            '--create',
                            action='store_true',
                            help='create new user')
        parser.add_argument('-d',
                            '--delete',
                            type=str,
                            action='store',
                            metavar='USERNAME',
                            help='delete user')
        parser.add_argument('-r',
                            '--regenerate-colors',
                            action='store_true',
                            help='Generate a random color for each user')
        parser.add_argument('-l',
                            '--list',
                            action='store_true',
                            help='list all users')
        parser.add_argument('-m',
                            '--modify',
                            type=str,
                            action='store',
                            metavar='USERNAME',
                            help='modify user')
        parser.add_argument('-s',
                            '--search',
                            type=str,
                            action='store',
                            metavar='USERNAME',
                            help='search for user')
        args = parser.parse_args(argv[2:])

        # Process subcommands for user 
        if args.create:
            u = User()
            
            #: Inspect user model so we can get database column types later on
            insp = inspect(User)

            #: Automatically generated keys from the User model
            #keys = sorted(u.__dict__.keys()[1:])

            #: Manually created list of keys in appropriate order
            keys = ['nickname', 'email', 'full_name', 'private_full_name', 
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

        elif args.delete:
            try:
                to_del = User.query.filter_by(nickname=args.delete).first()
                to_del.delete()
                print(bcolors.OKGREEN + 'User ' + args.delete + \
                      ' deleted successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.list:
            try:
                users = User.query.all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['id', 'nickname', 'email', 'full_name', 'private_full_name', 
                    'is_admin', 'phone', 'zip', 'employer']
            table_data = [keys]
            for u in users:
                usr = []
                for k in keys:
                    attr = getattr(u, k)
                    usr.append(('None' if attr is None else str(attr)))
                table_data.append(usr)
            table = AsciiTable(table_data)
            print(table.table)
            exit(0)

        elif args.modify:
            try:
                u = User.query.filter_by(nickname=args.modify).first()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)
            
            #: Inspect user model so we can get database column types later on
            insp = inspect(User)

            #: Automatically generated keys from the User model
            #keys = sorted(u.__dict__.keys()[1:])

            #: Manually created list of keys in appropriate order
            keys = ['nickname', 'email', 'full_name', 'private_full_name', 
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


        elif args.search:
            try:
                usr_sr = User.query.filter_by(nickname=args.search).all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['id', 'nickname', 'email', 'full_name', 'private_full_name', 
                    'is_admin', 'phone', 'zip', 'employer']
            table_data = [keys]
            for u in usr_sr:
                usr = []
                for k in keys:
                    attr = getattr(u, k)
                    usr.append(('None' if attr is None else str(attr)))
                table_data.append(usr)
            table = AsciiTable(table_data)
            print(table.table)

        elif args.regenerate_colors:
            for user in User.query.all():
                user.generate_color()

        else:
            parser.print_help()
            exit(0)

    def cause(self):
        '''Create, delete, modify or list causes. 
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  create, delete, modify or list causes'''),
            usage='''./app.py create [-c] [-d CAUSE] [-l] [-m CAUSE] [-s CAUSE]''')
        parser.add_argument('-c',
                            '--create',
                            action='store_true',
                            help='create new cause')
        parser.add_argument('-d',
                            '--delete',
                            type=str,
                            action='store',
                            metavar='SLUG',
                            help='delete cause')
        parser.add_argument('-l',
                            '--list',
                            action='store_true',
                            help='list all causes')
        parser.add_argument('-m',
                            '--modify',
                            type=str,
                            action='store',
                            metavar='SLUG',
                            help='modify cause')
        parser.add_argument('-s',
                            '--search',
                            type=str,
                            action='store',
                            metavar='SLUG',
                            help='search for cause')
        args = parser.parse_args(argv[2:])

        # Process subcommands for cause 
        if args.create:
            c = Cause()
            
            #: Inspect Cause model so we can get database column types later on
            insp = inspect(Cause)

            #: Automatically generated keys from the Cause model
            #keys = sorted(c.__dict__.keys()[1:])

            #: Manually created list of keys in appropriate order
            keys = ['title', 'boss', 'location', 'video', 'image',
                    'story_heading', 'story_content']

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

        elif args.delete:
            try:
                to_del = Cause.query.filter_by(slug=args.delete).first()
                to_del.delete()
                print(bcolors.OKGREEN + 'Cause ' + args.delete + \
                      ' deleted successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.list:
            try:
                causes = Cause.query.all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['id', 'title', 'slug', 'boss', 'location', 
                    'video', 'image', 'story_heading', 'story_content']
            table_data = [keys]
            for c in causes:
                cause = []
                for k in keys:
                    attr = getattr(c, k)
                    cause.append(('None' if attr is None else str(attr)))
                table_data.append(cause)
            table = AsciiTable(table_data)
            print(table.table)
            exit(0)

        elif args.modify:
            try:
                c = Cause.query.filter_by(slug=args.modify).first()
            except Exception as e:
                c = None
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)

            if c is None:
                print(bcolors.FAIL + 'Error: no cause found for slug "{0}"'.format(
                    args.modify
                ) + bcolors.ENDC)
                exit(1)
            
            #: Inspect user model so we can get database column types later on
            insp = inspect(Cause)

            #: Automatically generated keys from the Cause model
            #keys = sorted(c.__dict__.keys()[1:])

            #: Manually created list of keys in appropriate order
            keys = ['title', 'boss', 'location', 'video', 'image',
                    'story_heading', 'story_content']

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


        elif args.search:
            try:
                cause_sr = Cause.query.filter_by(slug=args.search).all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['id', 'title', 'slug', 'boss', 'location', 
                    'video', 'image', 'story_heading', 'story_content']
            table_data = [keys]
            for c in cause_sr:
                cause = []
                for k in keys:
                    attr = getattr(c, k)
                    cause.append(('None' if attr is None else str(attr)))
                table_data.append(cause)
            table = AsciiTable(table_data)
            print(table.table)

        else:
            parser.print_help()
            exit(0)

    def action(self):
        '''Create, delete, modify or list actions. 
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  create, delete, modify or list actions'''),
            usage='''./app.py action [-c] [-d ACTION] [-l] [-m ACTION] [-s ACTION]''')
        parser.add_argument('-c',
                            '--create',
                            action='store_true',
                            help='create new cause')
        parser.add_argument('-d',
                            '--delete',
                            type=str,
                            action='store',
                            help='delete cause')
        parser.add_argument('-l',
                            '--list',
                            action='store_true',
                            help='list all causes')
        parser.add_argument('-m',
                            '--modify',
                            type=str,
                            action='store',
                            help='modify cause')
        parser.add_argument('-s',
                            '--search',
                            type=str,
                            action='store',
                            help='search for cause')
        args = parser.parse_args(argv[2:])

        # Process subcommands for action 
        if args.create:
            a = Action()
            
            #: Inspect Cause model so we can get database column types later on
            insp = inspect(Action)

            #: Automatically generated keys from the Action model
            #keys = sorted(a.__dict__.keys()[1:])

            #: Manually created list of keys in appropriate order
            keys = ['cause_id', 'cause', 'title', 'description', 'expiration']

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

        elif args.delete:
            try:
                to_del = Action.query.filter_by(slug=args.delete).first()
                to_del.delete()
                print(bcolors.OKGREEN + 'Action ' + args.delete + \
                      ' deleted successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.list:
            try:
                actions = Action.query.all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['cause_id', 'cause', 'title', 'description', 'expiration']
            table_data = [keys]
            for a in actions:
                action = []
                for k in keys:
                    attr = getattr(a, k)
                    action.append(('None' if attr is None else str(attr)))
                table_data.append(action)
            table = AsciiTable(table_data)
            print(table.table)
            exit(0)

        elif args.modify:
            try:
                a = Action.query.filter_by(id=args.modify).first()
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


        elif args.search:
            try:
                action_sr = Action.query.filter_by(title=args.search).all()
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

            keys = ['cause_id', 'cause', 'title', 'description', 'expiration']
            table_data = [keys]
            for a in action_sr:
                action = []
                for k in keys:
                    attr = getattr(a, k)
                    cause.append(('None' if attr is None else str(attr)))
                table_data.append(action)
            table = AsciiTable(table_data)
            print(table.table)

        else:
            parser.print_help()
            exit(0)

    def clean(self):
        '''Clean python and vim temporary files.
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  clean up temporary files for python and/or vim'''),
            usage='''./app.py clean [-a] [-p] [-t]''')
        parser.add_argument('-a',
                            '--all',
                            action='store_true',
                            help='clean up both python and vim temporary files')
        parser.add_argument('-l',
                            '--list',
                            action='store_true',
                            help='list all files that can be removed')
        parser.add_argument('-p',
                            '--python',
                            action='store_true',
                            help='only clean python files')
        parser.add_argument('-t',
                            '--temp',
                            action='store_true',
                            help='only clean vim temporary files')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='verbose')
        args = parser.parse_args(argv[2:])

        # Process subcommands for clean
        verbose = args.verbose
        if args.all:
            dirt = DirtCleaner(verbose)
            try:
                dirt.find(['*.*.sw?', '*~', '*.pyc', '*.stackdump'])
                dirt.rem()
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.list:
            dirt = DirtCleaner(verbose)
            try:
                dirt.find(['*.*.sw?', '*~', '*.pyc', '*.stackdump'])
                dirt.lst()
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.python:
            dirt = DirtCleaner(verbose)
            try:
                dirt.find(['*.pyc', '*.stackdump'])
                dirt.rem()
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.temp:
            dirt = DirtCleaner(verbose)
            try:
                dirt.find(['*.*.sw?', '*~'])
                dirt.rem()
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        else:
            parser.print_help()
            exit(0)

    def run(self):
        '''Running the app.
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  run the Flask app'''),
            usage='''./app.py run [-h] [-H HOST] [-p PORT] [-d]''')
        parser.add_argument('-H',
                            '--host',
                            default='localhost',
                            action='store',
                            help='host name or IP')
        parser.add_argument('-p',
                            '--port',
                            type=int,
                            default=5000,
                            action='store',
                            help='port number')
        parser.add_argument('-d',
                            '--debug',
                            default=True,
                            action='store_true',
                            help='debug mode')
        parser.set_defaults(host='localhost', port=5000, debug=True)
        args = parser.parse_args(argv[2:])

        # Run the app. No need for a separate class.
        app.run(host=args.host, port=args.port, debug=args.debug)

    def test(self):
        '''Run unit tests for the app.
        '''
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=dedent('''\
                description:
                  run unit tests for the app'''),
            usage='''./app.py run [-h] [-a] [-m MODULE] [-v]''')
        parser.add_argument('-a',
                            '--all',
                            action='store_true',
                            help='test all')
        parser.add_argument('-m',
                            '--module',
                            action='store',
                            help='test a specific module')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='verbose')
        args = parser.parse_args(argv[2:])

        # If verbose flag is set, increase verbosity level to 2, otherwise leave
        # it as 1, which is default.
        verbosity = args.verbose and 2 or 1

        # Process subcommands for test 
        if args.all:
            try:
                suite = unittest.TestLoader() \
                                .discover(start_dir='.', pattern='test*.py')
                unittest.TextTestRunner(verbosity=verbosity).run(suite)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.module:
            try:
                suite = unittest.TestLoader() \
                                .loadTestsFromName('app.' + args.module + '.tests')
                unittest.TextTestRunner(verbosity=verbosity).run(suite)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        else:
            parser.print_help()
            exit(0)


class Database(object):
    '''Manipulates the database. Including creating, upgrading, downgrading and
    migrating. Each time app models are modified a db migration is necessary.
    '''
    def __init__(self, database_uri=None, migrate_repo=None):
        self.database_uri = database_uri
        self.migrate_repo = migrate_repo

    def get_version(self):
        '''Simply returns the current database version as an int.'''
        return api.db_version(self.database_uri, self.migrate_repo)

    def print_version(self):
        print('Current database version..: ' + str(self.get_version()))

    def create(self):
        '''Creates a database.
        '''
        db.create_all()
        if not path.exists(self.migrate_repo):
            api.create(self.migrate_repo, 'database repository')
            api.version_control(self.database_uri, self.migrate_repo)
        else:
            api.version_control(self.database_uri, self.migrate_repo, 
                                api.version(self.migrate_repo))

    def downgrade(self, amount):
        '''Downgrades database given amount of versions.
        '''
        v = self.get_version() 
        api.downgrade(self.database_uri, self.migrate_repo, v - amount)
        print('Database downgraded by....: ' + str(amount))
        self.print_version()

    def migrate(self):
        '''Creates SQLAlchemy migration by comparing the structure of the database
        (obtained from app.db) against the structure of the models (obtained from 
        models.py). The differences between the two are recorded as a migration
        script inside the migration repository. The migration script knows how to 
        apply a migration or undo it, so it is always possible to upgrade or
        downgrade the database format.
        '''
        v = self.get_version() 
        migration = self.migrate_repo + ('/versions/%03d_migration.py' % (v + 1))
        tmp_module = imp.new_module('old_model')
        old_model = api.create_model(self.database_uri, self.migrate_repo)
        exec(old_model, tmp_module.__dict__)
        script = api.make_update_script_for_model(self.database_uri, 
                                                  self.migrate_repo, 
                                                  tmp_module.meta, 
                                                  db.metadata)
        open(migration, 'wt').write(script)
        api.upgrade(self.database_uri, self.migrate_repo)
        print('New migration saved as ...: ' + path.relpath(migration))
        self.print_version() 

    def upgrade(self, amount):
        ''' Upgrades the database to the latest version by applying the migration 
        scripts stored in database repository.
        '''
        v =  self.get_version()
        api.upgrade(self.database_uri, self.migrate_repo, v + amount)
        print('Database upgraded by......: ' + str(amount))
        self.print_version()


class Module(object):
    '''Lists existing modules or creates direcotory/file structure for new ones.
    '''
    @staticmethod
    def get_mods():
        '''Get all present modules and return them as a list.
        '''
        #: Get all directories in the app directory
        mods = walk('app').next()[1]
        # Remove static and template directories from the list
        mods.remove('static')
        mods.remove('templates')
        return mods 

    def print_mods(self):
        print('Modules present...........: ' + ', '.join(self.get_mods()))

    @staticmethod
    def create(name):
        '''Create the new module file structure and some initial files.
        '''
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


class DirtCleaner(object):
    '''Finds/deletes temporary and compiled pyc files.
    '''
    def __init__(self, verbose, start_dir=None, dirt=None):
        self.verbose = verbose
        self.start_dir = '.'
        self.dirt = [] 

    def find(self, file_types):
        for t in file_types:
            for root, dirs, files in walk(self.start_dir):
                for file in fnmatch.filter(files, t):
                    self.dirt.append(path.join(root, file))

    def lst(self):
        if len(self.dirt) and self.verbose:
            for file in self.dirt:
                print(file)
        elif len(self.dirt) and not self.verbose:
            print(bcolors.OKGREEN + 'Found ' + \
                  str(len(self.dirt)) + ' files' + bcolors.ENDC)
        else:
            print('Nothing found')

    def rem(self):
        if len(self.dirt) and self.verbose:
            for file in self.dirt:
                print('rm ' + file)
                remove(file)
        elif len(self.dirt) and not self.verbose:
            for file in self.dirt:
                remove(file)
            print(bcolors.OKGREEN + 'Removed ' + \
                  str(len(self.dirt)) + ' files' + bcolors.ENDC)
        else:
            print('Nothing to remove')
        

if __name__ == '__main__':
    AppManager() 

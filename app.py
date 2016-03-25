#!venv/bin/python
#
# Name........: app.py
# Author......: Pavel Mamontov
# Version.....: 0.1
# Description.: Unified manager for Flask apps. Manipulates database, creates
#               modules, runs the app in Werkzeug.
# License.....: GPLv3 (see LICENSE file)
#
import argparse, imp
from sys import argv
from os import path, walk, listdir, makedirs
from app import app, db
from migrate.exceptions import DatabaseAlreadyControlledError
from migrate.versioning import api
from app.config.local import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from textwrap import dedent


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
              mod         create new module scaffolding 
              run         run the Flask app
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
        database = Database(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        if args.version:
            database.print_version()
            exit(0)

        elif args.create:
            print('Creating database...')
            try:
                database.create()
                print(bcolors.OKGREEN + 'Database app.db created successfully' + bcolors.ENDC)
                exit(0)
            except DatabaseAlreadyControlledError:
                print(bcolors.FAIL + 'Error: Database already exists for this project' + bcolors.ENDC)
                exit(1)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.downgrade:
            print('Downgrading database by ' + str(args.downgrade) + ' version(s)...')
            try:
                database.downgrade(args.downgrade)
                print(bcolors.OKGREEN + 'Database downgraded successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.migrate:
            print('Migrating database...')
            try:
                database.migrate()
                print(bcolors.OKGREEN + 'Database migrated successfully' + bcolors.ENDC)
                exit(0)
            except Exception as e:
                print(bcolors.FAIL + 'Error: ' + str(e) + bcolors.ENDC)
                exit(1)

        elif args.upgrade:
            print('Upgrading database by ' + str(args.upgrade) + ' version(s)...')
            try:
                database.upgrade(args.upgrade)
                print(bcolors.OKGREEN + 'Database upgraded successfully' + bcolors.ENDC)
                exit(0)
            except KeyError:
                print (bcolors.FAIL + 'Error: Already at most recent version' + bcolors.ENDC)
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
                print(bcolors.OKGREEN + 'Module ' + args.name + ' created successfully' + bcolors.ENDC)
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
        app/models.py). The differences between the two are recorded as a migration
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
        print(bcolors.WARNING + "Don\'t forget to register your module blueprint in " + \
              bcolors.BOLD + "app/__init__.py " + bcolors.ENDC + \
              bcolors.WARNING + "like so:" + bcolors.ENDC)
        print('  from app.' + name + '.views import mod as ' + name + 'Module')  
        print('  app.register_blueprint(' + name + 'Module)')


if __name__ == '__main__':
    AppManager() 

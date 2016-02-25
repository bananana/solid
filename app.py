#!venv/bin/python
#
#
#
import sys, argparse, textwrap
import os.path
from app import app, db
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AppManager(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            usage=textwrap.dedent('''\
            ./app.py [-h] [command]

            commands:
              db          manipluate the database
              mod         create new module from a template
              run         run the Flask app
            '''))
        parser.add_argument('command', help='subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)
        getattr(self, args.command) ()

    def db(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
                description: 
                  manipulates the databse'''),
            usage='''./app.py db [-h] [-c] [-d] [-m] [-u]''')
        parser.add_argument('-c', 
                            '--create', 
                            action='store_true', 
                            help='create database with SQLAlchemy')
        parser.add_argument('-d', 
                            '--downgrade',
                            nargs='?',
                            const=1,
                            action='store', 
                            help='downgrade database')
        parser.add_argument('-m', 
                            '--migrate', 
                            action='store_true', 
                            help='migrate database')
        parser.add_argument('-u', 
                            '--upgrade',
                            nargs='?',
                            const=1,
                            action='store', 
                            help='upgrade database')
        parser.set_defaults(downgrade=1, upgrade=1)
        args = parser.parse_args(sys.argv[2:])
        #: Database object defined below
        database = Database(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
        if args.create:
            print 'Creating database...'
            database.create()
            print bcolors.OKGREEN + 'Database app.db created successfully' + bcolors.ENDC
        elif args.downgrade:
            print 'Downgrading database...'
            database.downgrade(args.downgrade)
        elif args.migrate:
            print 'Migrating database...'
        elif args.upgrade:
            print 'Upgrading database...'
        else:
            parser.print_help()

    def mod(self):
        parser=argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
                description: 
                  create new module'''),
            usage='''./app.py mod [-h] [-c NAME]''')
        parser.add_argument('-n', 
                            '--name',
                            '-c',
                            '--create',
                            nargs='?',
                            const='new_module',
                            action='store', 
                            help='create module')
        args = parser.parse_args(sys.argv[2:])
        print 'Creating module {name}'.format(name=args.name)

    def run(self):
        parser=argparse.ArgumentParser(
            description='run the Flask app',
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
        args = parser.parse_args(sys.argv[2:])
        app.run(host=args.host, port=args.port, debug=args.debug)


class Database(object):
        
    def __init__(self, database_uri=None, migrate_repo=None):
        self.database_uri = database_uri
        self.migrate_repo = migrate_repo

    def get_version(self):
        return str(api.db_version(self.database_uri, self.migrate_repo))

    def create(self):
        '''Create a database with SQLAlchemy.'''
        db.create_all()
        if not os.path.exists(self.migrate_repo):
            api.create(self.migrate_repo, 'database repository')
            api.version_control(self.database_uri, self.migrate_repo)
        else:
            api.version_control(self.database_uri, self.migrate_repo, 
                                api.version(self.migrate_repo))

    def downgrade(self, amount):
        '''Downgrades database given amount of versions.'''
        v = self.get_version() 
        if int(v) > 0:
            api.downgrade(self.database_uri, self.migrate_repo, int(v) - amount)
            v = self.get_version()
            print('Database downgraded by....: ' + amount)
            print('Current database version .: ' + v)
        else:
            print bcolors.FAIL + 'Already at the earliest possible version' + bcolors.ENDC
            print('Current database version .: ' + v)

    def migrate():
        '''Creates SQLAlchemy migration by comparing the structure of the database
        (obtained from app.db) against the structure of the models (obtained from 
        app/models.py). The differences between the two are recorded as a migration
        script inside the migration repository. The migration script knows how to 
        apply a migration or undo it, so it is always possible to upgrade or
        downgrade the database format.'''
        '''
        v = api.db_version(self.migrate_repo, self.migrate_repo)
        migration = self.migrate_repo + ('/versions/%03d_migration.py' % (v+1))
        tmp_module = imp.new_module('old_model')
        old_model = api.create_model(self.migrate_repo, self.migrate_repo)
        exec(old_model, tmp_module.__dict__)
        script = api.make_update_script_for_model(self.migrate_repo, 
                                                  self.migrate_repo, 
                                                  tmp_module.meta, db.metadata)
        open(migration, 'wt').write(script)
        api.upgrade(self.migrate_repo, self.migrate_repo)
        v = api.db_version(self.migrate_repo, self.migrate_repo)
        print('New migration saved as ...: ' + migration)
        print('Current database version .: ' + str(v))
        '''

    def upgrade():
        ''' Upgrades the database to the latest version by applying the migration 
         scripts stored in database repository.'''
        '''
        api.upgrade(self.migrate_repo, self.migrate_repo)
        v = api.db_version(self.migrate_repo, self.migrate_repo)
        print('Current database version .: ' + str(v)) 
        '''


if __name__ == '__main__':
    AppManager() 

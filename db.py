#!venv/bin/python
#
# A helper program to facilitate database maintenance of a Flask app using 
# SQLAlchemy. Based on scripts by Miguel Grinberg (blog.miguelgrinberg.com)
#
import sys, getopt, imp
import os.path
from app import db
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO

def help():
    print(
    '''
Usage:
    db.py [option]

Options:
    -h, --help      Display this help message.
    -c, --create    Create a database.
    -d, --downgrade Downgrade to previous version of database.
    -m, --migrate   Migrate database changes.
    -u, --upgrade   Upgrade to next version of database.
    ''')

def create():
    '''Create a database with SQLAlchemy.
    '''
    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, 
                            api.version(SQLALCHEMY_MIGRATE_REPO))

def downgrade():
    '''Downgrades database one version. Run multiple times to downgrade
    several versions.
    '''
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABSE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version .: ' + str(v)) 

def migrate():
    '''Creates SQLAlchemy migration by comparing the structure of the database
    (obtained from app.db) against the structure of the models (obtained from 
    app/models.py). The differences between the two are recorded as a migration
    script inside the migration repository. The migration script knows how to 
    apply a migration or undo it, so it is always possible to upgrade or
    downgrade the database format.
    '''
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    exec(old_model, tmp_module.__dict__)
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, 
                                          SQLALCHEMY_MIGRATE_REPO, 
                                          tmp_module.meta, db.metadata)
    open(migration, 'wt').write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ...: ' + migration)
    print('Current database version .: ' + str(v))

def upgrade():
    ''' Upgrades the database to the latest version by applying the migration 
    scripts stored in database repository.
    '''
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version .: ' + str(v)) 

def main(argv):
    try:
        opts, args = getopt.getopt(argv,'hcdmu')
    except getopt.GetoptError:
        help() 
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help() 
        elif opt in ('-c', '--create'):
            create() 
        elif opt in ('-d', '--downgrade'):
            downgrade() 
        elif opt in ('-m', '--migrate'):
            migrate() 
        elif opt in ('-u', '--upgrade'):
            upgrade() 

if __name__ == '__main__':
    main(sys.argv[1:])

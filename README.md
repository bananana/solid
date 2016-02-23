# solid

This app is still under heavy development. Name subject to change.

## Setup

First, clone the repo and install submodules

    git clone https://github.com/bananana/solid
    cd solid
    git submodule update --init

Then create a python virtual environment, install requirements and create a database

    virtualenv venv
    pip install -r requirements.txt
    ./db.py -create

## Running

    ./run.py
    
By default the app will run on *localhost:5000*. You can modify that in config.py. If you want to run the app in a virtual machine, you'll want to set host to 0.0.0.0

## Database
Using sqlite for now, to make development easier. If you modify models, you'll need to migrate the database:

    ./db.py --migrate

## Utilities
**run.py**

Runs the app using the Werkzeug server.

**db.py**

Manipulates the database using SQLAlchemy. Run *./db.py --help* for full documentation.

# TODO
* Combine run.py and db.py in one utility so everything is neater.
* Finish models
* Setup unit testing (per modlue or app-wide?)
* Documentation and proper comments
* So much more...

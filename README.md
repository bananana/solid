# solid

This app is still under heavy development. Name subject to change.

## Setup

First, clone the repo and install submodules

    git clone https://github.com/bananana/solid
    cd solid
    git submodule update --init

Then create and start  a python virtual environment, install requirements and create a database

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    ./app.py db --create

## Utilities

For now all app management is done through the `app.py` utility. To get help:

    ./app.py --help
    ./app.py db --help
    ./app.py mod --help
    ./app.py run --help

## Running the App

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or port:

    ./app.py run --host <HOST> --port <PORT>

## Database

Using sqlite for now, to make development easier. If you modify models, you'll need to migrate the database:

    ./app.py db --migrate

# TODO
* Finish models
* Replace python scripts with [Invoke](http://docs.pyinvoke.org/en/latest/) or similar.
* Setup unit testing (per modlue or app-wide?)
* Documentation and proper comments
* So much more...

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
    ./db.py --create

## Utilities

All app management is done from **app.py** script, for help run it without any arguments or like so:

    ./app.py -h

Currently you can manipulate the database (**db** command), create module scaffolding (**mod** command) and run the app (**run** command). Each command comes with a set of subcommands. Getting help for them is done the same way as with the main script.

    ./app.py db -h
    ./app.py mod -h
    ./app.py run -h

## Running the App

    ./app.py run

By default the app will run in debug mode on *localhost:5000*. You can modify that behavious with **-H**, **-p** and **-d** flags. If you want to run the app in a virtual machine, you'll want to set host to 0.0.0.0

## Database
Using sqlite for now, to make development easier. If you modify models, you'll need to migrate the database:

    ./app.py db -m

# TODO
* Finish models
* Setup unit testing (per modlue or app-wide?)
* Documentation and proper comments
* So much more...

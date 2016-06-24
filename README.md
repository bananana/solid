# solid

This app is still under heavy development. Name subject to change.

## Setup

First, clone the repo and install submodules

    git clone https://github.com/bananana/solid
    cd solid
    git submodule update --init

Then create and start a python virtual environment, install requirements and
create a database

    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    ./app.py db --create

**Note** `Flask-Misaka` requires that the following packages are installed on
your computer: `gcc`, `libffi-dev`, `python-dev` and `python-cffi`. Make sure
you install them using your distro's package manager before running `pip install
-r requirements.txt`.

## Running the App

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or
port:

    ./app.py run --host <HOST> --port <PORT>

or edit `app/config/local.py` to change the default local (development)
settings.

## Utilities

For now all app management is done through the `app.py` utility. To get help:

    $ ./app.py --help
    $ ./app.py cause --help
    $ ./app.py user --help
    $ ./app.py db --help
    $ ./app.py mod --help
    $ ./app.py run --help
    $ ./app.py test --help

## Deployment

You will additionally need `make` and `git-archive-all` 
(`pip install git-archive-all`). Then edit `Makefile` and set `SSH_HOST` and
`SSH_USER` for your server, and run

    $ make

(you will need to enter your `sudo` password, if one is required, a few times)

## [Contributing](CONTRIBUTING.md)

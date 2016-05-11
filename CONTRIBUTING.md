# Contributing

## Workflow

Since the app is still in heavy development we're using
[GitFlow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
workflow, at least till the first stable release.

What this means in a nutshell:

* Master branch is for releases (and release hotfixes), so don't branch off or push to it directly.
* Branch off **dev** and merge into it when a feature is complete.
* A separate branch called **release-0.0.0** would be used to prepare a release.

## Styleguide

We're using [Pocoo Styleguide](http://flask.pocoo.org/docs/0.10/styleguide/).

## Getting Started 

Clone the repository and install dependencies:

    git clone https://github.com/bananana/solid
    cd solid
    git submodule update --init
    virtualenv venv
    . venv/bin/activate
    pip install -r requirement.txt

**Note** `Flask-Misaka` requires that the following packages are installed on your computer: `gcc`, `libffi-dev`, `python-dev` and `python-cffi`. Make sure you install them using your distro's package manager before running `pip install -r requirements.txt`.

For now all app management is done through the `app.py` utility. To get help:

    ./app.py -h
    ./app.py cause -h
    ./app.py user -h
    ./app.py db -h
    ./app.py mod -h
    ./app.py run -h
    ./app.py test -h

If you have just cloned the project, you'll need to create a database:

    ./app.py db -c

If you modify models, you'll have to migrate the database, so it reflects your changes:

    ./app.py db -m

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or port:

    ./app.py run -H <HOST> -p <PORT>

or edit `app/config/local.py` to change the default local (development)
settings.

You can create users and cause straight from the command line, to do so run:
    
    ./app.py user -c
    ./app.py cause -c

## Configuration

To change project-wide settings, edit `app/config/base.py`. To add per-instance
settings, create a new `app/config/INSTANCE.py` (with 
`from app.config.base import *` at the top) and set the `FLASK_CONFIG`
environment variable to specify loading that file.

## Making Changes 

Checkout the dev branch and create your feature branch:

    git checkout -b your-feature dev

Work on your feature, run tests to make sure it doesn't break anything. If
you're an official collaborator you can merge back into **dev** when you're
done:

    git pull origin dev
    git checkout dev
    git merge your-feature
    git push
    git branch -d your-feature

If you're not an official collaborator, submit a pull request for your
enhancement, bugfix or feature.

## Unit Testing

Unit tests are organized on per module basis with `tests_base.py` being reused
by all of them. If you add a feature, don't forget to add a test for it in the
appropriate module. Also, run all tests before you push your changes to the
remote. 

To run test on all modules do:

    ./app.py test -a 

To run tests for a particular module (like *users* module) do:

    ./app.py test -m users 

For verbose mode, pass a -v flag:

    ./app.py test -a -v

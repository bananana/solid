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

**Note** `Flask-Misaka` requires that the following packages are installed on
your computer: `gcc`, `libffi-dev`, `python-dev` and `python-cffi`. Make sure
you install them using your distro's package manager before running `pip install
-r requirements.txt`.

The app comes with a demo database, `demo.db` -- to use it, copy `demo.db` to
`app.db`. The password for the "admin" user is "far=dreary8title".

## Running the App

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or
port:

    ./app.py runserver --host <HOST> --port <PORT>

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

## Translations

Translations for Spanish are included -- to view, set your browser language to
Spanish or change the drop-down (globe icon, top-right) to "es".

### Static (interface) text

Using `Flask-Babel`. 

#### To translate new text 

_(e.g. if you are adding text to the interface)_

 * For text in Python files, e.g. flash messages and e-mail subjects, define
     `_()` with `from flask_babel import gettext as _`, then use it to wrap
     strings e.g. change `'Cause created!'` to `_('Cause created!')`
 * For text in HTML, just wrap text in the `_()` method, e.g. change 
   `Stand with us` to `{{ _('Stand with us!') }}`
 * Run `make i18n` to find text and add it to the translation catalogue
 * Fill in the catalogue with translations
 * Run `make i18n_compile` to compile the catalogue
 * Restart your local server

### Dynamic (app) text

Using `sqlalchemy_i18n`. 

#### To make a model translatable

 1. Rename the model fields you want to translate, e.g. `Foo.title` becomes
     `Foo._title`, and add a `FooTranslation` class with a `translation_base`
     subclass (see `app/pages/models.py` for an example of the latter)
 1. Create a new database migration with `./app.py db migrate`, edit it so
     that column deletions / additions become renames (e.g. see
     `migrations/versions/f4984bdb99ec_.py`), and run it with `./app.py db upgrade`
 1. Start a blank migration with `./app.py db revision` and copy / adapt an
     existing data migration, e.g.  `migrations/versions/4a490dacaa06_.py`, to
     copy content from `Foo` to `FooTranslation`. NB you need to
     manually define tables with the relevant field names in the migration; if
     you reference the `Foo` definition in the app then the migration will break
     when the tables change (i.e. in the next step). Optionally, write a
     `downgrade()` method to reverse the change.
 1. Run your migration with `./app.py db upgrade`. Check in the database that the
     field content has been saved as new `FooTranslation` rows.
 1. Remove the renamed fields on `Foo`, e.g. `Foo._title`, generate a new
    migration with `./app.py db migrate` and run it with `./app.py db upgrade`

If you have a `wtforms.ext.sqlalchemy.orm.model_form` for this model:

 1. Edit the `only` option of the `FooForm` to remove the translated fields
 1. Create a new `FooTranslationForm` with the translated fields (see e.g.
    `app/pages/forms.py`)
 1. Edit your `foo_add()` and `foo_update()` views to instantiate a
    `FooTranslationForm`, add it to context as `form_trans`, populate it from
    `request.form` (which holds data for both forms; the name is a coincidence),
    add `form_trans.validate_on_submit()` to the conditional, and then call
    `form_trans.populate(foo)` to copy form data from `form_trans` to the object
 1. For `foo_add()`, you need to manually create a `FooTranslation` instance,
    call `form_trans.populate(foo_translation)` instead, and manually assign it
    as the fallback translation with `foo.fallback_translation = foo_translation`
    -- this avoids a crash caused when a `Foo` has a Spanish but no English
    version.
 1. Edit the `foo_form.html` template to load relevant fields from `form_trans`
    instead of `form`

## Deployment

You will additionally need `make` and `git-archive-all` 
(`pip install git-archive-all`). Then edit `Makefile` and set `SSH_HOST` and
`SSH_USER` for your server, and run

    $ make

(you will need to enter your `sudo` password, if one is required, a few times)

To deploy to a different project root, e.g. for a staging version, define
`ROOT`, e.g.

    $ make ROOT=/var/www/bsolid_staging

(you may also wish to override `CONFIG`)

## [Contributing](CONTRIBUTING.md)

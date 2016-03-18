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

You'll need to export OAuth environment variables in order for sicial login to work. Edit the `envvars.sh` file and add OAuth ids and secrets. Alternatively, you can manually export the variables without storing them in a file. The app will work without these variables being set but social login won't work. To export the environment variables from a file run the following after starting virtualenv:

    . envvars.sh

Or export them manually like so:

    export OAUTH_GOOGLE_ID=your-oauth-google-id
    export OAUTH_GOOGLE_SECRET=your-oauth-google-secret
    export OAUTH_TWITTER_ID=your-oauth-twitter-id
    export OAUTH_TWITTER_SECRET=your-oauth-twitter-secret
    export OAUTHLIB_INSECURE_TRANSPORT=1
    export OAUTHLIB_RELAX_TOKEN_SCOPE=1

The last two variables should only be used for development, **do not use them in production**.

For now all app management is done through the `app.py` utility. To get help:

    ./app.py -h
    ./app.py db -h
    ./app.py mod -h
    ./app.py run -h

If you have just cloned the project, you'll need to create a database:

    ./app.py db -c

If you modify models, you'll have to migrate the database, so it reflects your changes:

    ./app.py db -m

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or port:

    ./app.py run -H <HOST> -p <PORT>

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

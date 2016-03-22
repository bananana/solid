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


## Running the App

To run the app:

    ./app.py run

By default the app will run on *localhost:5000*. To run on a different host or port:

    ./app.py run --host <HOST> --port <PORT>

## Utilities

For now all app management is done through the `app.py` utility. To get help:

    ./app.py --help
    ./app.py db --help
    ./app.py mod --help
    ./app.py run --help

## [Contributing](CONTRIBUTING.md)

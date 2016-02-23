#!venv/bin/python
from app import app
from config import HOST, PORT, DEBUG

app.run(host=HOST, debug=DEBUG)

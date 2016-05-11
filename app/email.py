from threading import Thread

from flask import render_template
from flask.ext.mail import Message

from app import app, mail

def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, context, template_text, template_html=None, sender=None):
    """ sends an email using Flask-Mail (in the background using threads) """
    msg = Message(subject, sender=sender, recipients=recipients)

    if sender is not None:
        msg.sender = sender

    msg.body = render_template(template_text, **context)

    if template_html is not None:
        msg.html = render_template(template_html, **context)

    thr = Thread(target=_send_async_email, args=[app, msg])
    thr.start()

from threading import Thread

from flask import render_template

from flask_mailgun.message import Message

from app import app, mailgun


def _send_async_email(app, msg):
    with app.app_context():
        r = mailgun.send(msg)


def send_email(subject, recipients, context, template_text, template_html=None, sender=None, bcc=None):
    """ sends an email using Flask-Mail (in the background using threads) """
    # clear blank recipients
    recipients = [r for r in recipients if r != '' and r is not None]

    if len(recipients) > 1:
        bcc = list(recipients)
        recipients = [app.config['DEFAULT_EMAIL_SENDER'],]

    if sender is not None:
        msg.sender = sender

    msg = Message(subject, sender=sender, recipients=recipients, bcc=bcc)

    msg.body = render_template(template_text, **context)

    if template_html is not None:
        msg.html = render_template(template_html, **context)

    thr = Thread(target=_send_async_email, args=[app, msg])
    thr.start()

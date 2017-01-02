from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from . import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, template, **kwargs):
    print("Begin send mail")
    print(to)
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
            sender='web_admin@yeah.net', recipients=[to])
    msg.body = render_template( template + '.txt', **kwargs)
    msg.html = render_template( template + '.html', **kwargs)
    thr = Thread( target=send_async_email, args = [app, msg])
    thr.start()
    return thr
import app

from app import mail
from flask_mail import Message

def sendSignUpAuthMail(authUrl: str, email: str):
    msg = Message("Growler SignUp Auth Mail", sender=app.app.config['MAIL_USERNAME'], recipients = [email])
    msg.body = f'Auth Link : http://3.17.36.195/signUpAuth/{authUrl}'
    app.mail.send(msg)

def sendLoginAuthMail(loginKey: int, email: str):
    msg = Message("Growler Login Auth Mail", sender=app.app.config['MAIL_USERNAME'], recipients = [email])
    msg.body = f'Login Key : {loginKey}'
    app.mail.send(msg)

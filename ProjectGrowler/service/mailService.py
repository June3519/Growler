from ProjectGrowler import mail, config
from flask_mail import Message

def sendSignUpAuthMail(authUrl: str, email: str):
    msg = Message("Growler SignUp Auth Mail", sender=config['MAIL_USERNAME'], recipients = [email])
    msg.body = f'Auth Link : http://3.17.36.195/signUpAuth/{authUrl}'
    mail.send(msg)

def sendLoginAuthMail(loginKey: int, email: str):
    msg = Message("Growler Login Auth Mail", sender=config['MAIL_USERNAME'], recipients = [email])
    msg.body = f'Login Key : {loginKey}'
    mail.send(msg)

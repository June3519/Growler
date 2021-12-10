from ProjectGrowler import mail, config
from flask_mail import Message


# 메일인증 메일 보내기
def sendSignUpAuthMail(authUrl: str, email: str):
    msg = Message("Growler SignUp Auth Mail", sender=config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Auth Link : https://3.17.36.195/signUpAuth/{authUrl}'
    mail.send(msg)


# 로그인 인증키 메일 보내기
def sendLoginAuthMail(loginKey: int, email: str):
    msg = Message("Growler Login Auth Mail", sender=config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Login Key : {loginKey}'
    mail.send(msg)

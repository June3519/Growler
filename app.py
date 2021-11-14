from flask import Flask, render_template, request, redirect, abort, session, flash, url_for
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask import make_response, jsonify

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Gjwns1168512!@3.17.36.195:3306/growler"
app.secret_key = 'growler_random_key_plz'

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "jslee8196@gmail.com"
app.config["MAIL_PASSWORD"] = "qlalfdld"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)

mail = Mail(app)

from service.userService import *
from forms.loginForm import LoginForm
from forms.signUpForm import SignUpForm
from forms.loginAuthForm import LoginAuthForm

if __name__ == '__main__':
    app.run()


@app.route('/')
@login_required
def index():
    return 'Login Success'


@app.route('/logout')
@login_required
def logout():
    session.pop("NickName")
    return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        errorMessage, user = loginWithAuthKey(form.email.data, form.password.data, form.authNumber.data)
        if errorMessage is not None:
            flash(errorMessage, 'danger')
        else:
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    if form.validate_on_submit():
        if createUser(form.email.data, form.nickname.data, form.password.data):
            return redirect(url_for('signUpResult'))
        else:
            flash('already email or nickname', 'danger')
    else:
        if len(form.errors) != 0:
            flash(form.errors, "danger")

    return render_template('signUp.html', form=form)


@app.route('/signUpResult')
def signUpResult():
    return render_template('signUpResult.html')


@app.route('/signUpAuth/<certKey>')
def signUpAuth(certKey):
    if emailCert(certKey):
        return render_template('commonMessagePage.html', message='Complete Email Cert. Please Login')
    else:
        abort(404)


@app.route('/sendAuthKey', methods=['POST'])
def sendAuthKey():
    form = LoginAuthForm()

    loginErrorMessage = loginWithoutAuthKey(form.email.data, form.password.data)
    if loginErrorMessage is None:
        return make_response("Success", 200)
    else:
        return make_response(loginErrorMessage, 400)


# Login Handlers
@login_manager.user_loader
def user_loader(user_id):
    existsUser = findUserById(user_id)
    if existsUser is None:
        return None

    loginData = UserFlaskLoginData()
    loginData.id = existsUser.id
    loginData.nickName = existsUser.nickName

    return loginData

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")


# Default handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

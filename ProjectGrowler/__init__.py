from flask import Flask
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

db = SQLAlchemy()
mail = Mail()
config = None
login_manager = LoginManager()


def create_app() -> Flask:
    from . import allController
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Gjwns1168512!@3.17.36.195:3306/growler"
    app.secret_key = 'growler_random_key_plz'

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = "jhur3519@gmail.com"
    app.config["MAIL_PASSWORD"] = "Gjwns116!!"
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True

    app.config['FLASK_RUN_HOST'] = '0.0.0.0'
    app.config['FLASK_RUN_PORT'] = 443
    app.config['FLASK_RUN_CERT'] = 'adhoc'

    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(allController.blue_allController)
    global config
    config = app.config

    return app


@login_manager.user_loader
def user_loader(user_id):
    from ProjectGrowler.service.userService import findUserById
    existsUser = findUserById(user_id)
    if existsUser is None:
        return None

    from ProjectGrowler.models.userModel import UserFlaskLoginData
    loginData = UserFlaskLoginData()
    loginData.id = existsUser.id
    loginData.nickName = existsUser.nickName

    return loginData


@login_manager.unauthorized_handler
def unauthorized():
    from flask import redirect
    return redirect("/login")

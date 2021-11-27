from flask import Blueprint, render_template, request, redirect, abort, session, flash, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user, login_manager

blue_allController = Blueprint("All", __name__, url_prefix="")


@blue_allController.route('/')
@login_required
def index():
    return render_template('index.html')


@blue_allController.route('/users/<nickName>')
@login_required
def indexFromUser(nickName):
    return render_template('index.html', nickName=nickName)


@blue_allController.route('/growl', methods=['POST'])
@login_required
def createPost():
    from ProjectGrowler.service.growlService import createNewPost
    params = request.get_json()
    createNewPost(current_user.id, params['message'], params['tags'])

    return "", 200


@blue_allController.route('/growl', methods=['GET'])
@login_required
def getRecentPostsByCurrentUser():
    from ProjectGrowler.service.growlService import getPostsByNickName
    result = getPostsByNickName(current_user.nickName)
    if result is None:
        return "Unknown User NickName", 404
    else:
        return jsonify(result), 200


@blue_allController.route('/growl/<nickName>', methods=['GET'])
@login_required
def getRecentPostsByNickName(nickName):
    from ProjectGrowler.service.growlService import getPostsByNickName
    result = getPostsByNickName(nickName)
    if result is None:
        return "Unknown User NickName", 404
    else:
        return jsonify(result), 200


@blue_allController.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("All.login"))


@blue_allController.route('/login', methods=['GET', 'POST'])
def login():
    from ProjectGrowler.forms.loginForm import LoginForm
    form = LoginForm()
    if form.validate_on_submit():
        from ProjectGrowler.service.userService import loginWithAuthKey
        errorMessage, user = loginWithAuthKey(form.email.data, form.password.data, form.authNumber.data)
        if errorMessage is not None:
            flash(errorMessage, 'danger')
        else:
            login_user(user)
            return redirect(url_for('All.index'))

    return render_template('login.html', form=form)


@blue_allController.route('/signUp', methods=['GET', 'POST'])
def signUp():
    from ProjectGrowler.forms.signUpForm import SignUpForm
    from ProjectGrowler.service.userService import createUser

    form = SignUpForm()
    if form.validate_on_submit():

        if createUser(form.email.data, form.nickname.data, form.password.data):
            return redirect(url_for('All.signUpResult'))
        else:
            flash('already email or nickname', 'danger')
    else:
        if len(form.errors) != 0:
            flash(form.errors, "danger")

    return render_template('signUp.html', form=form)


@blue_allController.route('/signUpResult')
def signUpResult():
    return render_template('signUpResult.html')


@blue_allController.route('/signUpAuth/<certKey>')
def signUpAuth(certKey):
    from ProjectGrowler.service.userService import emailCert
    if emailCert(certKey):
        return render_template('commonMessagePage.html', message='Complete Email Cert. Please Login')
    else:
        abort(404)


@blue_allController.route('/sendAuthKey', methods=['POST'])
def sendAuthKey():
    from ProjectGrowler.forms.loginAuthForm import LoginAuthForm
    from flask import make_response
    from ProjectGrowler.service.userService import loginWithoutAuthKey

    form = LoginAuthForm()

    loginErrorMessage = loginWithoutAuthKey(form.email.data, form.password.data)
    if loginErrorMessage is None:
        return make_response("Success", 200)
    else:
        return make_response(loginErrorMessage, 400)


# Default handlers
@blue_allController.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
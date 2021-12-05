import json

from flask import Blueprint, render_template, request, redirect, abort, session, flash, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user, login_manager

blue_allController = Blueprint("All", __name__, url_prefix="")


@blue_allController.route('/')
@login_required
def index():
    return render_template('index.html', following=False)


@blue_allController.route('/users/<nickName>')
@login_required
def indexFromUser(nickName):
    if current_user.nickName.casefold() == nickName.casefold():
        return redirect(url_for("All.index"))

    from ProjectGrowler.service.userService import isFollowing
    fow = isFollowing(current_user.id, nickName)
    return render_template('index.html', nickName=nickName, following=fow)


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


@blue_allController.route('/follow/<nickName>', methods=['PUT'])
def addFollower(nickName):
    from ProjectGrowler.service.userService import followUser
    message, success = followUser(current_user.id, nickName)

    if success:
        return message, 200
    else:
        return message, 403


@blue_allController.route('/unfollow/<nickName>', methods=['DELETE'])
def deleteFollower(nickName):
    from ProjectGrowler.service.userService import unfollowUser
    message, success = unfollowUser(current_user.id, nickName)

    if success:
        return message, 200
    else:
        return message, 403


@blue_allController.route('/dm/<nickName>')
@login_required
def directMessage(nickName):
    if current_user.nickName.casefold() == nickName.casefold():
        return redirect(url_for("All.directMessageList"))

    from ProjectGrowler.service.dmService import getDMRoom
    dmRoomId = getDMRoom(current_user.id, nickName)
    if dmRoomId == False:
        return "Unknown NickName", 404
    else:
        return render_template('dm.html', roomId=dmRoomId, myId=current_user.id)


@blue_allController.route('/dm/recent/<roomId>')
@login_required
def getRecentDM(roomId):
    from ProjectGrowler.service.dmService import getDirectMessages
    messages = getDirectMessages(roomId)

    return jsonify(messages)


@blue_allController.route('/dm/<roomId>', methods=['POST'])
@login_required
def newDmMessage(roomId):
    from ProjectGrowler.service.dmService import postNewDirectMessage
    params = request.get_json()
    postNewDirectMessage(current_user.id, roomId, params["message"])

    return "Ok", 200


@blue_allController.route('/dm')
@login_required
def directMessageList():
    from ProjectGrowler.service.dmService import getDMRoomList
    roomList = getDMRoomList(current_user.id)

    return render_template('dmlist.html', roomList=json.dumps(roomList))


@blue_allController.route('/chats')
@login_required
def chatRoomList():
    from ProjectGrowler.service.chatService import getChatRoomList
    roomList = getChatRoomList(current_user.id)

    return render_template('chatlist.html', roomList=json.dumps(roomList))


@blue_allController.route('/chats/recent/<roomId>')
@login_required
def getRecentChat(roomId):
    from ProjectGrowler.service.chatService import getChatMessages
    messages = getChatMessages(roomId)

    return jsonify(messages)


@blue_allController.route('/chats/<tag>')
@login_required
def chatMessages(tag):
    from ProjectGrowler.service.chatService import getChatRoom
    chatRoomId = getChatRoom(current_user.id, tag)

    if chatRoomId == False:
        return "Unknown Tag", 404
    else:
        return render_template('chat.html', roomId=chatRoomId, myId=current_user.id)



@blue_allController.route('/chats/<roomId>', methods=['POST'])
@login_required
def newChatMessage(roomId):
    from ProjectGrowler.service.chatService import postNewChatMessage
    params = request.get_json()
    postNewChatMessage(current_user.id, roomId, params["message"])

    return "Ok", 200


# Default handlers
@blue_allController.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

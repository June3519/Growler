import json

from flask import Blueprint, render_template, request, redirect, abort, session, flash, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user, login_manager

blue_allController = Blueprint("All", __name__, url_prefix="")


# 내 타임라인
@blue_allController.route('/')
@login_required
def index():
    return render_template('index.html', following=False)


# 다른사람 타임라인
@blue_allController.route('/users/<nickName>')
@login_required
def indexFromUser(nickName):
    if current_user.nickName.casefold() == nickName.casefold():
        return redirect(url_for("All.index"))

    from ProjectGrowler.service.userService import isFollowing
    fow = isFollowing(current_user.id, nickName)
    return render_template('index.html', nickName=nickName, following=fow)


# 글 post api
@blue_allController.route('/growl', methods=['POST'])
@login_required
def createPost():
    from ProjectGrowler.service.growlService import createNewPost
    params = request.get_json()
    createNewPost(current_user.id, params['message'], params['tags'])

    return "", 200


# 글 가져오기 api
@blue_allController.route('/growl', methods=['GET'])
@login_required
def getRecentPostsByCurrentUser():
    from ProjectGrowler.service.growlService import getPostsByNickName
    result = getPostsByNickName(current_user.nickName)
    if result is None:
        return "Unknown User NickName", 404
    else:
        return jsonify(result), 200


# 다른사람 타임라인 글 가져오기 api
@blue_allController.route('/growl/<nickName>', methods=['GET'])
@login_required
def getRecentPostsByNickName(nickName):
    from ProjectGrowler.service.growlService import getPostsByNickName
    result = getPostsByNickName(nickName)
    if result is None:
        return "Unknown User NickName", 404
    else:
        return jsonify(result), 200


# 로그아웃
@blue_allController.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("All.login"))


# 로그인 페이지
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


# 가입 페이지
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


# 가입 결과 페이지
@blue_allController.route('/signUpResult')
def signUpResult():
    return render_template('signUpResult.html')


# 이메일 인증 페이지
@blue_allController.route('/signUpAuth/<certKey>')
def signUpAuth(certKey):
    from ProjectGrowler.service.userService import emailCert
    if emailCert(certKey):
        return render_template('commonMessagePage.html', message='Complete Email Cert. Please Login')
    else:
        abort(404)


# 인증키 요청 api
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


# 팔로워 추가
@blue_allController.route('/follow/<nickName>', methods=['PUT'])
def addFollower(nickName):
    from ProjectGrowler.service.userService import followUser
    message, success = followUser(current_user.id, nickName)

    if success:
        return message, 200
    else:
        return message, 403


# 팔로워 삭제
@blue_allController.route('/unfollow/<nickName>', methods=['DELETE'])
def deleteFollower(nickName):
    from ProjectGrowler.service.userService import unfollowUser
    message, success = unfollowUser(current_user.id, nickName)

    if success:
        return message, 200
    else:
        return message, 403


# 1:1대화창
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


# 1:1대화 글 가져오기 api
@blue_allController.route('/dm/recent/<roomId>')
@login_required
def getRecentDM(roomId):
    from ProjectGrowler.service.dmService import getDirectMessages
    messages = getDirectMessages(roomId)

    return jsonify(messages)


# 1:1 대화 전송 api
@blue_allController.route('/dm/<roomId>', methods=['POST'])
@login_required
def newDmMessage(roomId):
    from ProjectGrowler.service.dmService import postNewDirectMessage
    params = request.get_json()
    postNewDirectMessage(current_user.id, roomId, params["message"])

    return "Ok", 200


# 1:1 대화 목록 가져오기
@blue_allController.route('/dm')
@login_required
def directMessageList():
    from ProjectGrowler.service.dmService import getDMRoomList
    roomList = getDMRoomList(current_user.id)

    return render_template('dmlist.html', roomList=json.dumps(roomList))


# 채팅 목록 가져오기
@blue_allController.route('/chats')
@login_required
def chatRoomList():
    from ProjectGrowler.service.chatService import getChatRoomList
    roomList = getChatRoomList(current_user.id)

    return render_template('chatlist.html', roomList=json.dumps(roomList))


# 채팅창 글 가져오기 api
@blue_allController.route('/chats/recent/<roomId>')
@login_required
def getRecentChat(roomId):
    from ProjectGrowler.service.chatService import getChatMessages
    messages = getChatMessages(roomId)

    return jsonify(messages)


# 채팅 페이지
@blue_allController.route('/chats/<tag>')
@login_required
def chatMessages(tag):
    from ProjectGrowler.service.chatService import getChatRoom
    chatRoomId = getChatRoom(current_user.id, tag)

    if chatRoomId == False:
        return "Unknown Tag", 404
    else:
        return render_template('chat.html', roomId=chatRoomId, myId=current_user.id)


# 채팅 글 보내기 api
@blue_allController.route('/chats/<roomId>', methods=['POST'])
@login_required
def newChatMessage(roomId):
    from ProjectGrowler.service.chatService import postNewChatMessage
    params = request.get_json()
    postNewChatMessage(current_user.id, roomId, params["message"])

    return "Ok", 200


# 패스워드 리셋 요청 페이지
@blue_allController.route('/forgotpassword', methods=['GET', 'POST'])
@login_required
def forgotpassword():
    from ProjectGrowler.forms.forgotpasswordForm import forgotpasswordForm
    form = forgotpasswordForm()

    if form.validate_on_submit():
        from ProjectGrowler.service.userService import setPasswordResetInfo
        if setPasswordResetInfo(form.email.data):
            return redirect(url_for('All.signUpResult'))
        else:
            flash('unknown email nickname', 'danger')
    else:
        if len(form.errors) != 0:
            flash(form.errors, "danger")

    return render_template('forgotpassword.html', form=form)


# 패스워드 변경 페이지
@blue_allController.route('/resetpassword/<resetKey>', methods=['GET', 'POST'])
@login_required
def resetpassword(resetKey):
    from ProjectGrowler.forms.resetPasswordForm import resetPasswordForm
    form = resetPasswordForm()

    if form.validate_on_submit():
        from ProjectGrowler.service.userService import resetPassword
        if resetPassword(form.resetKey.data, form.password.data):
            return redirect(url_for('All.signUpResult'))
        else:
            flash('Url is invalid', 'danger')
    else:
        if len(form.errors) != 0:
            flash(form.errors, "danger")

    return render_template('resetpassword.html', form=form, resetKey=resetKey)


# Default handlers
@blue_allController.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

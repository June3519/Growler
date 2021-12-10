import sys

from sqlalchemy import or_
from ProjectGrowler import db
from ProjectGrowler.models.follower import FollowerModel
from ProjectGrowler.models.userModel import UserModel, UserFlaskLoginData
from ProjectGrowler.models.userEmailCert import UserEmailCertModel
from ProjectGrowler.models.userLoginAuth import UserLoginAuthModel
from ProjectGrowler.service.mailService import sendSignUpAuthMail, sendLoginAuthMail, sendPasswordResetMail
from datetime import timedelta, datetime

import string
import random
import hashlib


# 새 유저 생성
def createUser(email: str, nickName: str, password: str) -> bool:
    session = db.session.begin().session

    try:
        existsUser = session.query(UserModel).filter(
            or_(UserModel.email == email, UserModel.nickName == nickName)).first()

        if existsUser == None:
            newUser = UserModel(
                email=email,
                nickName=nickName,
                password=hashlib.sha256(password.encode()).hexdigest(),
                isMailCert=False
            )

            session.add(newUser)
            session.flush()

            newRandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

            newEmailCert = UserEmailCertModel(
                userId=newUser.id,
                linkUrl=newRandomString
            )

            session.add(newEmailCert)
            sendSignUpAuthMail(newRandomString, email)

            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        print(e, file=sys.stderr)
        return False
    finally:
        session.close()


# 이메일 인증하기 
def emailCert(certKey: str) -> bool:
    session = db.session.begin().session
    try:
        emailCertData = session.query(UserEmailCertModel).filter(UserEmailCertModel.linkUrl == certKey).first()
        if emailCertData != None:
            emailCertData.user.isMailCert = True
            session.delete(emailCertData)
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


# 로그인 ID PW 인증하고 인증키 메일 보내기
def loginWithoutAuthKey(email: str, password: str) -> str:
    session = db.session.begin().session
    try:
        existsUser = session.query(UserModel).filter(
            UserModel.email == email, UserModel.password == hashlib.sha256(password.encode()).hexdigest()).first()

        if existsUser is None:
            return "Wrong Email or Password"

        if existsUser.isMailCert == False:
            return "EMail Not Certed"

        n = random.randint(100000, 999999)
        expireTime = datetime.now() + timedelta(minutes=5)

        existsLoginAuth = session.query(UserLoginAuthModel).filter(
            UserLoginAuthModel.userId == existsUser.id).first()

        if existsLoginAuth is None:
            existsLoginAuth = UserLoginAuthModel()
            existsLoginAuth.userId = existsUser.id
            session.add(existsLoginAuth)

        existsLoginAuth.authNumber = n
        existsLoginAuth.expireTime = expireTime

        session.commit()
        sendLoginAuthMail(n, existsUser.email)

        return None
    except Exception as e:
        session.rollback()
        return e
    finally:
        session.close()


# ID로 유저 찾기
def findUserById(userId: int) -> UserModel:
    session = db.session.begin().session
    try:
        existsUser = session.query(UserModel).filter(UserModel.id == userId).first()
        return existsUser
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


# 인증키를 포함하여 진짜 로그인 하기
def loginWithAuthKey(email: str, password: str, authKey: int) -> str:
    session = db.session.begin().session
    try:
        existsUser = session.query(UserModel).filter(
            UserModel.email == email, UserModel.password == hashlib.sha256(password.encode()).hexdigest()).first()

        if existsUser is None:
            return "Wrong Email or Password", None

        if existsUser.isMailCert == False:
            return "EMail Not Certed", None

        existsLoginAuth = session.query(UserLoginAuthModel).filter(
            UserLoginAuthModel.userId == existsUser.id).first()

        if existsLoginAuth is None:
            return "Require Auth Key Send", None

        if existsLoginAuth.authNumber != authKey:
            return "Auth Key Error", None

        if existsLoginAuth.expireTime < datetime.now():
            return "Auth Key Expired. Require ReAuth", None

        session.commit()
        loginData = UserFlaskLoginData()
        loginData.id = existsUser.id
        loginData.nickName = existsUser.nickName
        return None, loginData

    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()


# 팔로우 유저
def followUser(currentUserId: int, targetUserNickName: str) -> bool:
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.id == currentUserId).first()

        targetUser = session.query(UserModel).filter(
            UserModel.nickName == targetUserNickName).first()

        if currentUser is None:
            return "Wrong Current User", False

        if targetUser is None:
            return "Wrong Target User NickName", False

        existsFollowInfo = session.query(FollowerModel).filter(
            (FollowerModel.userId == currentUser.id) & (FollowerModel.targetUserId == targetUser.id)).first()

        if existsFollowInfo is None:
            newFollowInfo = FollowerModel(
                userId=currentUser.id,
                targetUserId=targetUser.id
            )
            session.add(newFollowInfo)

        session.commit()
        return "Follow Success", True

    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()


# 팔로우 취소
def unfollowUser(currentUserId: int, targetUserNickName: str) -> bool:
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.id == currentUserId).first()

        targetUser = session.query(UserModel).filter(
            UserModel.nickName == targetUserNickName).first()

        if currentUser is None:
            return "Wrong Current User", False

        if targetUser is None:
            return "Wrong Target User NickName", False

        existsFollowInfo = session.query(FollowerModel).filter(
            (FollowerModel.userId == currentUser.id) & (FollowerModel.targetUserId == targetUser.id)).first()

        if existsFollowInfo is not None:
            session.delete(existsFollowInfo)

        session.commit()
        return "UnFollow Success", True

    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()


# 팔로잉 여부 가져오기
def isFollowing(currentUserId: int, targetUserNickName: str) -> bool:
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.id == currentUserId).first()

        targetUser = session.query(UserModel).filter(
            UserModel.nickName == targetUserNickName).first()

        if currentUser is None:
            return False

        if targetUser is None:
            return False

        existsFollowInfo = session.query(FollowerModel).filter(
            (FollowerModel.userId == currentUser.id) & (FollowerModel.targetUserId == targetUser.id)).first()

        session.commit()

        if existsFollowInfo is None:
            return False
        else:
            return True

    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()


# 패스워드 리셋 메일 보내기
def setPasswordResetInfo(email: str) -> bool:
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.email == email).first()

        if currentUser is None:
            return False

        newRandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        currentUser.resetpassword = newRandomString

        sendPasswordResetMail(newRandomString, email)
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()


# 패스워드 리셋하기
def resetPassword(resetKey: str, newPassword: str) -> bool:
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.resetpassword == resetKey).first()

        if currentUser is None:
            return False

        currentUser.resetpassword = None
        currentUser.password = hashlib.sha256(newPassword.encode()).hexdigest()

        session.commit()

        return True
    except Exception as e:
        session.rollback()
        return e, None
    finally:
        session.close()

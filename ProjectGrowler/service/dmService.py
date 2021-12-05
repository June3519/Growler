from sqlalchemy import desc

from ProjectGrowler import db
from ProjectGrowler.models.directMessage import DirectMessageModel, DirectMessageTextModel, DirectMessageTextModelSchema
from ProjectGrowler.models.userModel import UserModel


def getDMRoom(currentUserId: int, targetUserNickName: str):
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

        existsDMRoom = session.query(DirectMessageModel).filter(
            (
                    (DirectMessageModel.sendUserId == currentUser.id) &
                    (DirectMessageModel.recvUserId == targetUser.id)
            ) |
            (
                    (DirectMessageModel.sendUserId == targetUser.id) &
                    (DirectMessageModel.recvUserId == currentUser.id)
            )
        ).first()

        if existsDMRoom is None:
            newDMRoom = DirectMessageModel(
                sendUserId=currentUser.id,
                recvUserId=targetUser.id,
            )

            session.add(newDMRoom)
            existsDMRoom = newDMRoom

        session.commit()
        return existsDMRoom.id
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def getDirectMessages(roomId: int):
    session = db.session.begin().session

    try:
        messages = session.query(DirectMessageTextModel).filter(
            DirectMessageTextModel.directMessageId == roomId).all()

        result = DirectMessageTextModelSchema(many=True).dump(messages)

        session.commit()
        return result
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def getDMRoomList(currentUserId: int):
    session = db.session.begin().session

    try:
        existsDMRoom = session.query(DirectMessageModel).filter(
            (
                    (DirectMessageModel.sendUserId == currentUserId) |
                    (DirectMessageModel.recvUserId == currentUserId)
            )
        ).all()

        resultLists = list()
        for room in existsDMRoom:
            if room.sendUserId != currentUserId:
                resultLists.append(
                    {
                        "nickName": room.sendUser.nickName,
                        "recentMessage": session.query(DirectMessageTextModel).filter(
                            DirectMessageTextModel.directMessageId == room.id).order_by(
                            desc(DirectMessageTextModel.id)).first()
                    })
            if room.recvUserId != currentUserId:
                recentMessageData = session.query(DirectMessageTextModel).filter(
                    DirectMessageTextModel.directMessageId == room.id).order_by(
                    desc(DirectMessageTextModel.id)).first()

                recentMsgString = '';
                if recentMessageData is not None:
                    recentMsgString = recentMessageData.directMessageTexts

                resultLists.append(
                    {
                        "nickName": room.recvUser.nickName,
                        "recentMessage": recentMsgString
                    })

        session.commit()
        return resultLists
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def postNewDirectMessage(currentUserId: int, roomId: int, message: str):
    session = db.session.begin().session

    try:
        newText = DirectMessageTextModel(
            directMessageId=roomId,
            senderUserId=currentUserId,
            directMessageTexts=message
        )

        session.add(newText)
        session.commit()
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

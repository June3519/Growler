from sqlalchemy import desc

from ProjectGrowler import db
from ProjectGrowler.models.chat import ChatRoomModel, UserChatRoomMapperModel, ChatRoomTextModel, \
    ChatRoomTextModelSchema
from ProjectGrowler.models.directMessage import DirectMessageModel, DirectMessageTextModel, DirectMessageTextModelSchema
from ProjectGrowler.models.userModel import UserModel


# 채팅방 찾기
def getChatRoom(currentUserId: int, tag: str):
    session = db.session.begin().session

    try:
        currentUser = session.query(UserModel).filter(
            UserModel.id == currentUserId).first()

        targetRoom = session.query(ChatRoomModel).filter(
            ChatRoomModel.roomTag == tag).first()

        if targetRoom is None:
            targetRoom = ChatRoomModel(
                roomTag=tag
            )
            session.add(targetRoom)
            session.flush()

        existsMapper = session.query(UserChatRoomMapperModel).filter(
            (
                    (UserChatRoomMapperModel.chatRoomId == targetRoom.id) &
                    (UserChatRoomMapperModel.userId == currentUserId)
            )
        ).first()

        if existsMapper is None:
            existsMapper = UserChatRoomMapperModel(
                chatRoomId=targetRoom.id,
                userId=currentUserId
            )

            session.add(existsMapper)
            session.flush()

        session.commit()
        return targetRoom.id
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


# 채팅 내용 가져오기
def getChatMessages(roomId: int):
    session = db.session.begin().session

    try:
        messages = session.query(ChatRoomTextModel).filter(
            ChatRoomTextModel.chatRoomId == roomId).all()

        result = ChatRoomTextModelSchema(many=True).dump(messages)

        session.commit()
        return result
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


# 채팅방 목록 가져오기
def getChatRoomList(currentUserId: int):
    session = db.session.begin().session

    try:
        mapperList = session.query(UserChatRoomMapperModel).filter(
            UserChatRoomMapperModel.userId == currentUserId
        ).all()

        resultLists = list()

        for mapper in mapperList:
                resultLists.append(
                    {
                        "tag": mapper.chatRoom.roomTag
                    })
        session.commit()
        return resultLists
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


#채팅방 메시지 보내기
def postNewChatMessage(currentUserId: int, roomId: int, message: str):
    session = db.session.begin().session

    try:
        newText = ChatRoomTextModel(
            chatRoomId=roomId,
            userId=currentUserId,
            chatMessageTexts=message
        )

        session.add(newText)
        session.commit()
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()

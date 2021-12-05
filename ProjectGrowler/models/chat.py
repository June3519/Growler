from datetime import datetime, timedelta

from marshmallow_sqlalchemy import fields

from ProjectGrowler import db

import marshmallow_sqlalchemy as ma

from ProjectGrowler.models.userModel import UserModelSchema


class ChatRoomModel(db.Model):
    __tablename__ = 'chat_rooms'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    roomTag = db.Column(db.String(64))

    chatList = db.relationship("ChatRoomTextModel")

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class UserChatRoomMapperModel(db.Model):
    __tablename__ = 'user_chatRoom_mappers'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    chatRoomId = db.Column(db.BigInteger, db.ForeignKey("chat_rooms.id"))
    chatRoom = db.relationship("ChatRoomModel", foreign_keys='UserChatRoomMapperModel.chatRoomId')
    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class ChatRoomTextModel(db.Model):
    __tablename__ = 'chatRoom_texts'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    chatRoomId = db.Column(db.BigInteger, db.ForeignKey("chat_rooms.id"))
    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    senderUser = db.relationship("UserModel", foreign_keys='ChatRoomTextModel.userId')

    chatMessageTexts = db.Column(db.String(4096))

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class ChatRoomTextModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ChatRoomTextModel
        load_instance = True
        include_relationships = True
    senderUser = fields.Nested(UserModelSchema)

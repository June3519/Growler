from datetime import datetime, timedelta
from ProjectGrowler import db

import marshmallow_sqlalchemy as ma


class DirectMessageModel(db.Model):
    __tablename__ = 'direct_messages'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    sendUserId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    sendUser = db.relationship("UserModel", foreign_keys='DirectMessageModel.sendUserId')
    recvUserId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    recvUser = db.relationship("UserModel", foreign_keys='DirectMessageModel.recvUserId')

    dmList = db.relationship("DirectMessageTextModel")

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class DirectMessageTextModel(db.Model):
    __tablename__ = 'direct_message_texts'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    directMessageId = db.Column(db.BigInteger, db.ForeignKey("direct_messages.id"))
    senderUserId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    senderUser = db.relationship("UserModel", foreign_keys='DirectMessageTextModel.senderUserId')

    directMessageTexts = db.Column(db.String(4096))

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class DirectMessageTextModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DirectMessageTextModel
        load_instance = True
        include_relationships = True

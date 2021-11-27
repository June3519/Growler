from ProjectGrowler import db
from datetime import datetime


class UserLoginAuthModel(db.Model):
    __tablename__ = 'user_login_auths'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.BigInteger, primary_key=True)
    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    user = db.relationship("UserModel", foreign_keys='UserLoginAuthModel.userId')
    authNumber = db.Column(db.Integer)
    expireTime = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

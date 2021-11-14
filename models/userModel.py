from app import db
from datetime import datetime
from flask_login import UserMixin

class UserModel(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255))
    nickName = db.Column(db.String(64))
    password = db.Column(db.String(255))
    isMailCert = db.Column(db.Boolean)

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class UserFlaskLoginData(UserMixin):
    id = 0
    nickName = ''

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
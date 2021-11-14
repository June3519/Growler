from app import db
from datetime import datetime

class UserEmailCertModel(db.Model):
    __tablename__ = 'user_email_certs'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.BigInteger, primary_key=True)

    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    user = db.relationship("UserModel", foreign_keys='UserEmailCertModel.userId')
    linkUrl = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


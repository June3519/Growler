from datetime import datetime, timedelta
from ProjectGrowler import db


class FollowerModel(db.Model):
    __tablename__ = 'followers'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    targetUserId = db.Column(db.BigInteger, db.ForeignKey("users.id"))

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

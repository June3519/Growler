from dataclasses import dataclass
from datetime import datetime, timedelta
from ProjectGrowler import db

import marshmallow_sqlalchemy as ma

class GrowlTagModel(db.Model):
    __tablename__ = 'growl_tags'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    growlId = db.Column(db.BigInteger, db.ForeignKey("growls.id"))
    tag = db.Column(db.String(4096))

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class GrowlTagModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GrowlTagModel
        load_instance = True
        include_relationships = True

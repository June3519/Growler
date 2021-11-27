from datetime import datetime, timedelta

from marshmallow.fields import List
from marshmallow_sqlalchemy import fields

from ProjectGrowler import db
import marshmallow_sqlalchemy as ma

from ProjectGrowler.models.growlTag import GrowlTagModel, GrowlTagModelSchema
from ProjectGrowler.models.userModel import UserModelSchema


class GrowlModel(db.Model):
    __tablename__ = 'growls'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    id = db.Column(db.BigInteger, primary_key=True)
    userId = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    user = db.relationship("UserModel", foreign_keys='GrowlModel.userId')
    growlText = db.Column(db.String(4096))
    tagList = db.relationship("GrowlTagModel")

    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class GrowlModelWithNestedTagListSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GrowlModel
        load_instance = True
        include_relationships = True

    user = fields.Nested(UserModelSchema)
    tagList = List(fields.Nested(lambda: GrowlTagModelSchema()))

from sqlalchemy import *
from ProjectGrowler import db
from sqlalchemy import *
from ProjectGrowler.models.growl import *
from ProjectGrowler.models.growlTag import *
from ProjectGrowler.models.userModel import UserModel


def createNewPost(userId: int, growlText: str, tags: str):
    session = db.session.begin().session
    try:
        newPost = GrowlModel(
            userId=userId,
            growlText=growlText,
        )

        session.add(newPost)
        session.flush()

        tags = tags.strip()
        if bool(tags):
            tagList = tags.split()
            tagList = list(dict.fromkeys(tagList))  # remove duplicate
            for tag in tagList:
                newTags = GrowlTagModel(
                    growlId=newPost.id,
                    tag=tag
                )
                session.add(newTags)

        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def getPosts(userId: int):
    session = db.session.begin().session
    try:
        posts = session.query(GrowlModel).filter(
            GrowlModel.userId == userId).order_by(desc(GrowlModel.id)).all()
        result = GrowlModelWithNestedTagListSchema(many=True).dump(posts)
        return result
    except Exception as e:
        session.rollback()
    finally:
        session.close()


def getPostsByNickName(nickName: str):
    session = db.session.begin().session
    try:
        findUser = session.query(UserModel).filter(
            UserModel.nickName == nickName
        ).first()

        if findUser is None:
            return None

        posts = session.query(GrowlModel).filter(
            GrowlModel.userId == findUser.id).order_by(desc(GrowlModel.id)).all()
        result = GrowlModelWithNestedTagListSchema(many=True).dump(posts)
        return result
    except Exception as e:
        session.rollback()
    finally:
        session.close()

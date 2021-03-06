from sqlalchemy import *
from ProjectGrowler import db
from sqlalchemy import *

from ProjectGrowler.models.follower import FollowerModel
from ProjectGrowler.models.growl import *
from ProjectGrowler.models.growlTag import *
from ProjectGrowler.models.userModel import UserModel


# 새글 쓰기
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


# 내 타임라인 글 가져오기
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


# 다른사람 타임라인글 가져오기
def getPostsByNickName(nickName: str):
    session = db.session.begin().session
    try:
        findUser = session.query(UserModel).filter(
            UserModel.nickName == nickName
        ).first()

        if findUser is None:
            return None

        followers = session.query(FollowerModel).filter(
            FollowerModel.userId == findUser.id
        ).all()

        idList = list(map(lambda u: u.targetUserId, followers))
        idList.append(findUser.id)

        posts = session.query(GrowlModel).filter(
             GrowlModel.userId.in_(idList)).order_by(desc(GrowlModel.id)).all()
        result = GrowlModelWithNestedTagListSchema(many=True).dump(posts)
        return result
    except Exception as e:
        session.rollback()
    finally:
        session.close()

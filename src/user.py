from flask_login import UserMixin

from src.db import get_db, close_db

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
    @staticmethod
    def get(user_id): # FIXME: Replace with better functionality...
        user = mongo.db.user.find_one({"id": user_id})
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        user = {
            "id": id_,
            "name": name,
            "email": email,
            "profile_pic": profile_pic
        }
        mongo.db.user.insert(user)

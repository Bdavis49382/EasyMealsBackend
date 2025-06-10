from firebase import db
from models.Household import User
from repositories.userRepository import UserRepository
from typing import Annotated
from fastapi import Depends

class UserController:
    def __init__(self, user_repo: Annotated[UserRepository, Depends()]):
        self.user_repo = user_repo

    def create_user(self, user: User):
        res = self.user_repo.create_user(user)
        if res == None:
            return None

        return user.google_id
    

    @staticmethod
    def create_user(user: User):
        res = db.collection('users').document(user.google_id).set( user.model_dump())
        if res == None:
            return None

        return user.google_id
    
    @staticmethod
    def get_user(user_id: str):
        # Get user data
        user = db.collection('users').document(user_id).get().to_dict()
        if user is None:
            return None
        if 'recipes' in user:
            # don't display the recipes
            user['recipes'] = f"{len(user['recipes'])} recipes"
        user['id'] = user_id
        return user

    @staticmethod
    def get_users(ids: list[str] | None = None):
        # Get all users
        users = db.collection('users').get()
        user_list = []
        for user_data in users:
            user = user_data.to_dict()
            # if a user wasn't found, or is not one we are looking for, move on.
            if user is None or (ids is not None and user_data.id not in ids):
                continue

            if 'recipes' in user:
                # don't display the recipes
                user['recipes'] = f"{len(user['recipes'])} recipes"
            user['id'] = user_data.id
            user_list.append(user)

        return user_list
    
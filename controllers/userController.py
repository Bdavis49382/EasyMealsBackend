from models.User import UserLite, User
from repositories.userRepository import UserRepository
from typing import Annotated
from fastapi import Depends

class UserController:
    def __init__(self, user_repo: Annotated[UserRepository, Depends()]):
        self.user_repo = user_repo

    def create_user(self, user: User):
        res = self.user_repo.create_user(user)
        return res
    
    def get_user(self, user_id: str) -> UserLite | None:
        user = self.user_repo.get_user(user_id)
        if user is None:
            return None
        return User.make_user_lite(user)
    
    def get_users(self, whitelist: list[str] | None = None) -> list[UserLite]:
        users = self.user_repo.get_users(whitelist)
        return [User.make_user_lite(user) for user in users]
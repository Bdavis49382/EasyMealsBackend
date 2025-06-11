from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove, FieldFilter, Or
from models.Household import Household, JoinCode
from models.User import User, UserLite
from controllers.userController import UserController
from typing import Annotated
from fastapi import Depends
from repositories.householdRepository import HouseholdRepository
from repositories.userRepository import UserRepository
import string, random

class HouseholdController:
    def __init__(self, repo: Annotated[HouseholdRepository, Depends()], user_repo: Annotated[UserRepository, Depends()]):
        self.repo = repo
        self.user_repo = user_repo
    
    def get_household(self, household_id: str) -> Household:
        return self.repo.get_household(household_id)

    def get_household_users(self, household_id: str) -> list[UserLite]:
        users = self.user_repo.get_users(self.repo.get_user_ids(household_id))
        return [User.make_user_lite(user) for user in users]
    
    def find_household(self, user_id: str) -> str | None:
        return self.repo.find_household(user_id)
    
    def get_join_code(self, household_id: str) -> JoinCode:
        # Get the household code
        code: JoinCode | None = self.repo.get_join_code(household_id)

        # if the code is empty or expired, generate a new one
        if code == None or code.expiration_date < datetime.now(timezone.utc):
            def get_random_code():
                options = string.digits + string.ascii_letters
                return ''.join(random.choice(options) for _ in range(6))

            # Generate a new code
            expiration_date = datetime.now(timezone.utc) + timedelta(hours=1)
            code = JoinCode(
                code=get_random_code(),
                expiration_date=expiration_date
            )
            self.repo.update_code(household_id, code)
        return code
    
    def join_household(self, user_id: str, code: str) -> list[UserLite] | None:
        """
        Returns the list of users after the join.
        """
        household = self.repo.get_household_by_code(code)

        if self.user_repo.get_user(user_id) is None:
            return None
        if household is None:
            return None
        if household.join_code is None or household.join_code.code != code:
            return None
        if household.join_code.expiration_date < datetime.now(timezone.utc):
            return None
        household_id = household.id
        # Check if the user is already in a household
        old_household_id = self.repo.find_household(user_id)
        if old_household_id is not None:
            if old_household_id == household_id:
                users = self.user_repo.get_users(self.repo.get_user_ids(household_id))
                return [User.make_user_lite(user) for user in users]
            else:
                # Remove the user from their current household
                self.kick_user(old_household_id, user_id)

        self.repo.add_user(household_id, user_id)
        users = self.user_repo.get_users(self.repo.get_user_ids(household_id))
        return [User.make_user_lite(user) for user in users]
    
    def kick_user(self,household_id: str, user_id: str) -> list[UserLite] | None:
        """
        Returns the list of users after the kick.
        """
        user_ids = self.repo.get_user_ids(household_id)
        # if this is the household owned by the user, it is deleted.
        if user_ids[0] == user_id:
            self.repo.delete_household(household_id)
            return None
        elif user_id in user_ids:
            self.repo.kick_user(household_id, user_id)
            users = self.user_repo.get_users(self.repo.get_user_ids(household_id))
            return [User.make_user_lite(user) for user in users]
        else:
            return None
        
    def create_household(self,user_id: str) -> str:
        return self.repo.create_household(user_id)
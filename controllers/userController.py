from firebase import db
from models.Household import User

class UserController:
    @staticmethod
    def create_user(user: User):
        ref = db.collection('users').add( user.model_dump())
        return ref[1].id
    
    @staticmethod
    def get_user(user_id: str):
        # Get user data
        user = db.collection('users').document(user_id).get().to_dict()
        if 'recipes' in user:
            # don't display the recipes
            user['recipes'] = f"{len(user['recipes'])} recipes"
        user['id'] = user_id
        if user is None:
            return None
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
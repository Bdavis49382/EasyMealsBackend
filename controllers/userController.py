from firebase import db
from models.Household import User

class UserController:
    def create_user(user: User):
        ref = db.collection('users').add( user.model_dump())
        return ref[1].id
    
    def get_user(user_id: str):
        # Get user data
        user = db.collection('users').document(user_id).get().to_dict()
        if user is None:
            return None
        return user
    
    def get_users():
        # Get all users
        users = db.collection('users').get()
        user_list = []
        for user_data in users:
            user = user_data.to_dict()
            if 'recipes' in user:
                # don't display the recipes
                user['recipes'] = f"{len(user['recipes'])} recipes"
            user['id'] = user_data.id
            user_list.append(user)

        return user_list
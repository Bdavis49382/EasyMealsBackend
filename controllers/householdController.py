from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove, FieldFilter
from models.Household import Household
import string, random

class HouseholdController:
    @staticmethod
    def get_household(household_id: str):
        ref = db.collection('households').document(household_id)
        return ref.get().to_dict()

    @staticmethod
    def find_household(user_id: str):
        # Find the household that the user is in
        households = db.collection('households').where('users', 'array_contains', user_id).get()
        if len(households) == 0:
            return None
        else:
            return households[0].id

    @staticmethod
    def create_household(user_id: str):
        # Create a new household
        household = Household()
        household.users.append(user_id)
        household_ref = db.collection('households').add( household.model_dump())
        return household_ref[1].id

    @staticmethod
    def get_household_code(household_id: str):
        # Get the household code
        household = db.collection('households').document(household_id).get().to_dict()
        code = None
        if 'join_code' in household and household['join_code'] is not None:
            code = household['join_code']

        # if the code is empty or expired, generate a new one
        if code == None or code['expiration_date'] < datetime.now(timezone.utc):
            def get_random_code():
                options = string.digits + string.ascii_letters
                return ''.join(random.choice(options) for _ in range(6))

            # Generate a new code
            expiration_date = datetime.now(timezone.utc) + timedelta(hours=1)
            code = {
                'code': get_random_code(),
                'expiration_date': expiration_date
            }
            db.collection('households').document(household_id).update({
                'join_code': code
            })
        return code

    @staticmethod
    def find_household_by_code(code: str):
        ref = db.collection('households').where(filter=FieldFilter("join_code","!=",None)).where(filter=FieldFilter("join_code.code","==",code))
        households = []
        for h in ref.get():
            h_dict = h.to_dict()
            h_dict['id'] = h.id
            households.append(h_dict)
        if len(households) == 1:
            return households[0]
        
        return None

    @staticmethod
    def join_household(user_id: str, code: str):
        household = HouseholdController.find_household_by_code(code)
        if household is None:
            return None
        if household['join_code'] is None or household['join_code']['code'] != code:
            return None
        if household['join_code']['expiration_date'] < datetime.now(timezone.utc):
            return None
        household_id = household['id']
        # Check if the user is already in a household
        old_household_id = HouseholdController.find_household(user_id)
        if old_household_id is not None:
            if old_household_id == household_id:
                return household_id
            else:
                # Remove the user from their current household
                HouseholdController.kick_user(old_household_id, user_id)

        db.collection('households').document(household_id).update({
            'users': ArrayUnion([user_id])
        })
        return household_id
    
    @staticmethod
    def kick_user(household_id: str, user_id: str):
        # Remove a user from a household
        db.collection('households').document(household_id).update({
            'users': ArrayRemove([user_id])
        })

        # Check if the user is the last one in the household
        household = db.collection('households').document(household_id).get().to_dict()
        if len(household['users']) == 0:
            db.collection('households').document(household_id).delete()
            return None
        else:
            return household_id
    

from firebase import db
from datetime import datetime, timezone, timedelta
from google.cloud.firestore_v1 import ArrayUnion
from models.Household import ShoppingItem

class ShoppingListController:
    def get_shopping_list(household_id: str):
        ref = db.collection('households').document(household_id)
        return ref.get().to_dict()["shopping_list"]

    def clean_list(household_id: str):
        ref = db.collection('households').document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        def item_is_valid(item):
            if 'time_checked' in item and item['time_checked'] is not None:
                if datetime.now(timezone.utc) - item['time_checked'] > timedelta(hours=12):
                    return False
            return True
        # if an item has been checked for more than 12 hours, remove it from the list
        initial_size = len(shopping_list)
        shopping_list = list(filter(item_is_valid, shopping_list))
        if len(shopping_list) < initial_size:
            ref.update({
                "shopping_list": shopping_list
            })

    def add_item(household_id, shopping_item: ShoppingItem):
        ref = db.collection('households').document(household_id)
        res = ref.update({
            "shopping_list": ArrayUnion([shopping_item.model_dump()])
        })
        return ref.get().to_dict()["shopping_list"]
    
    def add_items(household_id, shopping_items: list[ShoppingItem]):
        ref = db.collection('households').document(household_id)
        shopping_list = ref.get().to_dict()['shopping_list']
        shopping_list.extend(x.model_dump() for x in shopping_items)
        ref.update({"shopping_list": shopping_list})

    def check_item(household_id : str, index: int):
        ref = db.collection('households').document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        shopping_list[index]["checked"] = not shopping_list[index]["checked"]

        # track when the item was checked
        if shopping_list[index]["checked"]:
            shopping_list[index]["time_checked"] = datetime.now(timezone.utc)
        else:
            shopping_list[index]["time_checked"] = None

        ref.update({
            "shopping_list": shopping_list
        })
        return shopping_list

    def edit_item(household_id: str, index: int, shopping_item: ShoppingItem):
        ref = db.collection('households').document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        assert index < len(shopping_list), "Index out of range"

        shopping_list[index] = shopping_item.model_dump()
        ref.update({
            "shopping_list": shopping_list
        })
        return shopping_list

    def remove_item(household_id: str, index: int):
        ref = db.collection('households').document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        assert index < len(shopping_list), "Index out of range"

        shopping_list.pop(index)
        ref.update({
            "shopping_list": shopping_list
        })
        return shopping_list

    def wrap_items(item_strings: list[str], user_id: str, recipe_id: str) -> list[ShoppingItem]:
        return [ShoppingItem(name=x, user_id=user_id, recipe_id=recipe_id) for x in item_strings]
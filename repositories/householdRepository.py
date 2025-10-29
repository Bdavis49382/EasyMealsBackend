from models.User import User 
from models.Recipe import Recipe, RecipeOut, MenuItem
from models.ShoppingItem import ShoppingItem
from models.Household import Household, JoinCode
from firebase import household_ref
from fastapi import Depends, HTTPException
from typing import Annotated
from datetime import datetime, timezone
from uuid import uuid4
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove, FieldFilter, Or

class HouseholdRepository:
    def __init__(self, household_ref: Annotated[CollectionReference, Depends(household_ref)]):
        self.household_ref = household_ref
    
    def find_household(self,user_id: str) -> str | None:
        """
        Finds the id of the household which the user belongs in.
        Returns None if the user does not belong to one.
        """
        # Find the household that the user is in
        households = self.household_ref.where(filter=Or([
            FieldFilter('users', 'array_contains', user_id),
            FieldFilter('owner_id','==', user_id)
        ])).get()
        if len(households) == 0:
            return None
        else:
            return households[0].id

    def create_household(self,user_id: str) -> str:
        # Create a new household
        household = Household(owner_id=user_id)
        household_ref = self.household_ref.add( household.model_dump())
        return household_ref[1].id

    def get_join_code(self,household_id: str) -> JoinCode | None:
        return self.get_household(household_id).join_code
    
    def add_user(self, household_id: str, user_id: str) -> None:
        self.household_ref.document(household_id).update({
            'users': ArrayUnion([user_id])
        })

    def kick_user(self, household_id: str, user_id: str) -> None:
        self.household_ref.document(household_id).update({
            'users': ArrayRemove([user_id])
        })

    def delete_household(self, household_id: str) -> None:
        self.household_ref.document(household_id).delete()

    def get_household_by_code(self, code: str) -> Household | None:
        ref = self.household_ref.where(filter=FieldFilter("join_code","!=",None)).where(filter=FieldFilter("join_code.code","==",code))
        households = []
        for h in ref.get():
            h_dict = h.to_dict()
            h_dict['id'] = h.id
            households.append(h_dict)
        if len(households) == 1:
            return Household.model_validate(households[0])
        
        return None

    
    def update_code(self, household_id: str, new_code: JoinCode) -> None:
        self.household_ref.document(household_id).update({
            'join_code': new_code.model_dump()
        })

    def add_items(self, household_id: str, items: list[ShoppingItem]) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list: list = ref.get().to_dict()['shopping_list']
        for item in items:
            if item.id == None:
                item.id = uuid4().__str__()
            shopping_list.insert(0, item.model_dump())
        ref.update({"shopping_list": shopping_list})
    
    def add_item(self, household_id: str, item: ShoppingItem) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list: list = ref.get().to_dict()["shopping_list"]

        if item.id == None:
            item.id = uuid4().__str__()

        shopping_list.insert(0, item.model_dump())
        ref.update({
            "shopping_list": shopping_list
        })
    
    def get_household(self, household_id: str) -> Household:
        return Household.model_validate(self.household_ref.document(household_id).get().to_dict())
    
    def get_shopping_list(self, household_id: str) -> list[ShoppingItem]:
        household = self.get_household(household_id)
        return household.shopping_list
    
    def check_item(self, household_id: str, id: str) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list: list = ref.get().to_dict()["shopping_list"]

        try:
            index = [x["id"] for x in shopping_list].index(id)
        except:
            print(f'item with id {id} did not exist and so was not updated')
            raise HTTPException(status_code=400,detail="The checked item did not exist")

        shopping_list[index]["checked"] = not shopping_list[index]["checked"]

        # track when the item was checked
        if shopping_list[index]["checked"]:
            shopping_list[index]["time_checked"] = datetime.now(timezone.utc)
        else:
            shopping_list[index]["time_checked"] = None
        
        # Insert the checked item at the top of the checked items, whether it is now checked or unchecked
        checked = shopping_list.pop(index)
        new_index = -1
        for i,item in enumerate(shopping_list):
            if item["checked"]:
                new_index = i
                break
        if new_index == -1:
            shopping_list.append(checked)
        else:
            shopping_list.insert(new_index, checked)

        ref.update({
            "shopping_list": shopping_list
        })
    
    def update_item(self, household_id: str, id: str, item: ShoppingItem) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        try:
            index = [x["id"] for x in shopping_list].index(id)
        except:
            print(f'item with id {id} did not exist and so was not updated')
            raise HTTPException(status_code=400,detail="The updated item did not exist")


        shopping_list[index]['name'] = item.name
        ref.update({
            "shopping_list": shopping_list
        })
    
    def move_item(self, household_id: str, from_index: int, to_index: int) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list: list = ref.get().to_dict()["shopping_list"]

        shopping_list.insert(to_index,shopping_list.pop(from_index))
        ref.update({
            "shopping_list": shopping_list
        })
    
    def reorder_items(self, household_id: str, ordered_list: list[ShoppingItem]) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list: list = ref.get().to_dict()["shopping_list"]
        shopping_items: dict = {}
        out_list = []

        # put the content from the stored shopping list in the order of the ordered list
        for item in shopping_list:
            shopping_items[item["id"]] = item

        for item in ordered_list:
            if item.id in shopping_items and shopping_items[item.id]['checked'] == item.checked:
                out_list.append(shopping_items[item.id])
                del shopping_items[item.id]
        
        for item in shopping_items.values():
            if item['checked']:
                out_list.append(item)
            else:
                out_list.insert(0,item)
        
        ref.update({
            "shopping_list": out_list
        })


    def remove_item(self, household_id: str, index: int) -> None:
        ref = self.household_ref.document(household_id)
        shopping_list = ref.get().to_dict()["shopping_list"]

        shopping_list.pop(index)
        ref.update({
            "shopping_list": shopping_list
        })
    
    def remove_items(self, household_id: str, valid_condition):
        ref = self.household_ref.document(household_id)
        shopping_list = ref.get().to_dict()['shopping_list']

        initial_size = len(shopping_list)
        shopping_list = list(filter(valid_condition, shopping_list))
        if len(shopping_list) < initial_size:
            ref.update({
                "shopping_list": shopping_list
            })
    
    def get_menu_items(self, household_id: str) -> list[MenuItem]:
        return self.get_household(household_id).menu_recipes
    
    def add_recipe_to_menu(self, household_id: str, menu_item: MenuItem) -> None:
        ref = self.household_ref.document(household_id)
        ref.update({
            "menu_recipes": ArrayUnion([menu_item.model_dump()])
        })
    
    def get_menu_item_by_index(self, household_id: str, index: int) -> MenuItem:
        menu = self.get_household(household_id).menu_recipes
        assert index < len(menu), "Invalid index for menu item"
        return MenuItem.model_validate(menu[index])
    
    def get_user_ids(self, household_id: str) -> list[str]:
        household = self.get_household(household_id)
        return [household.owner_id, *household.users]
    
    def remove_menu_item(self, household_id: str, recipe_id: str) -> None:
        ref = self.household_ref.document(household_id)
        menu_items_raw = ref.get().to_dict()['menu_recipes']

        menu_items_raw = [x for x in menu_items_raw if x['recipe_id'] != recipe_id]
        ref.update({
            "menu_recipes" : menu_items_raw
        })

    def update_menu_item(self, household_id: str, index: int, updated: MenuItem) -> None:
        ref = self.household_ref.document(household_id)
        menu_items_raw = ref.get().to_dict()['menu_recipes']

        if menu_items_raw[index]['recipe_id'] == updated.recipe_id:
            menu_items_raw[index]['note'] = updated.note
            menu_items_raw[index]['date'] = updated.date
            ref.update({
                "menu_recipes" : menu_items_raw
            })

    def update_menu_item_by_recipe_id(self, household_id: str, recipe_id: str, updated: MenuItem) -> None:
        ref = self.household_ref.document(household_id)
        menu_items_raw = ref.get().to_dict()['menu_recipes']

        for menu_item in menu_items_raw:
            if menu_item['recipe_id'] == recipe_id:
                menu_item['note'] = updated.note
                menu_item['date'] = updated.date
                ref.update({
                    "menu_recipes" : menu_items_raw
                })
                break
    
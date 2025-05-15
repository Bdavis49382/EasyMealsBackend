from fastapi import APIRouter, Request
from models.Household import ShoppingItem
from controllers.householdController import HouseholdController

router = APIRouter(
    prefix="/household",
    tags= ["Household"]
)

@router.post("/create/{user_id}")
async def create_household(user_id: str):
    # Create a new household
    if HouseholdController.find_household(user_id) is not None:
        return {"message": "User already in a household"}
    household_id = HouseholdController.create_household(user_id)
    return {"message": "Household created successfully", "household_id": household_id}

@router.get("/get/{user_id}")
async def get_household_id(user_id: str):
    # Find the household that the user is in
    household_id = HouseholdController.find_household(user_id)
    if household_id is None:
        household_id = HouseholdController.create_household(user_id)
        return {"message": "Household created successfully", "household_id": household_id}
    return {"household_id": household_id}

@router.get("/code")
async def get_household_code(request: Request):
    code = HouseholdController.get_household_code(request.state.household_id)
    return {"code": code}

@router.get("/join/{household_id}/{user_id}/{code}")
async def join_household(household_id: str, user_id: str, code: str):
    result = HouseholdController.join_household(household_id, user_id, code)
    if result is None:
        return {"message": "Invalid household ID or code"}
    return {"household_id": result}

@router.delete("/kick/{user_id}")
async def kick_user(request: Request, user_id: str):
    result = HouseholdController.kick_user(request.state.household_id, user_id)
    if result is None:
        return {"message": "household removed"}
    return {"householdId": result}
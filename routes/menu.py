from fastapi import APIRouter, Request
from models.Recipe import Recipe
from controllers.feedController import FeedController

router = APIRouter(
    prefix="/menu",
    tags= ["Menu"]
)
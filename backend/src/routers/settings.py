from typing import Any, Dict

from fastapi import APIRouter
from robot_arm_controller.controller import ArmController

from utils.general import controller_dependency

router = APIRouter()


@router.get("/")
def get_items(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    return {"items": ["item1", "item2"]}


@router.post("/stop_movement/")
def stop_movement(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    controller.stop_movement()
    return {"message": "Movement stopped"}

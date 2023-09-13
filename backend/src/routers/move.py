from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel
from robot_arm_controller.control.arm_kinematics import ArmPose
from robot_arm_controller.controller import ArmController

from utils.general import controller_dependency

router = APIRouter()


class Move(BaseModel):
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float


# --------
# General
# --------


@router.post("/home/")
def home(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    print("Homing the arm in home endpoint")
    controller.home()
    return {"message": "Homed"}


# --------
# Pose
# --------


@router.post("/pose/move/")
def move(
    move: Move, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    move_dict = move.dict()
    pose = ArmPose(**move_dict)
    controller.move_to(pose)
    return {"message": "Moved"}


@router.get("/pose/current/")
def currentpose(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    pose = controller.current_pose
    return pose.as_dict


# --------
# Angle
# --------

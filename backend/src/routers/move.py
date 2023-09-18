from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
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
    wait: Optional[bool] = False


class Tool(BaseModel):
    toolValue: float
    wait: Optional[bool] = False


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
def move(move: Move, controller: ArmController = controller_dependency) -> JSONResponse:
    move_dict = move.dict()
    wait = move_dict.pop("wait")

    pose = ArmPose(**move_dict)

    move_is_possible = controller.move_to(pose)

    if wait:
        controller.wait_done_moving()
    if move_is_possible:
        return JSONResponse(content={"message": "Moved"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Not moved"}, status_code=400)


@router.get("/pose/current/")
def currentpose(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    pose = controller.current_pose
    pose_dict = pose.as_dict
    return pose_dict


@router.post("/tool/move/")
def tool_post(
    tool: Tool, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    tool_dict = tool.dict()
    tool_value = tool_dict["toolValue"]
    wait = tool_dict["wait"]
    controller.set_tool_value(tool_value)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


@router.get("/tool/current/")
def tool_get(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    tool_value = controller.tool_value

    return {"toolValue": tool_value}


@router.get("/status/")
def status(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    pose = controller.current_pose
    status_dict = pose.as_dict
    status_dict["toolValue"] = controller.tool_value
    status_dict["isHomed"] = controller.is_homed
    status_dict["moveQueueSize"] = controller.move_queue_size
    return status_dict


# --------
# Angle
# --------

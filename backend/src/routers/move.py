from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from robot_arm_controller.control.arm_kinematics import ArmPose
from robot_arm_controller.controller import ArmController

from utils.general import controller_dependency

router = APIRouter()

# --------
# Post Models
# --------


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


class MoveJoint(BaseModel):
    joint_idx: int
    joint_value: float
    wait: Optional[bool] = False


class HomeJoint(BaseModel):
    joint_idx: int
    wait: Optional[bool] = False


class MoveJoints(BaseModel):
    joint_values: list
    wait: Optional[bool] = False


# --------
# General
# --------


@router.post("/home/")
def home(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    print("Homing the arm in home endpoint")
    controller.home()
    return {"message": "Homed"}


@router.post("/home_joint/")
def home_joint(
    home_joint: HomeJoint, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    joint_idx = home_joint.model_dump().pop("joint_idx")
    controller.home_joint(joint_idx)
    return {"message": "Homed"}


# --------
# Pose
# --------


@router.post("/pose/")
def move(move: Move, controller: ArmController = controller_dependency) -> JSONResponse:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")

    pose = ArmPose(**move_dict)

    move_is_possible = controller.move_to(pose)

    if wait:
        controller.wait_done_moving()
    if move_is_possible:
        return JSONResponse(content={"message": "Moved"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Not moved"}, status_code=400)

@router.post("/pose/relative/")
def move_relative(move: Move, controller: ArmController = controller_dependency) -> JSONResponse:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")

    pose = ArmPose(**move_dict)

    move_is_possible = controller.move_to_relative(pose)

    if wait:
        controller.wait_done_moving()
    if move_is_possible:
        return JSONResponse(content={"message": "Moved"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Not moved"}, status_code=400)

@router.post("/pose/validate/")
def valid_pose(
    move: Move, controller: ArmController = controller_dependency
) -> JSONResponse:
    move_dict = move.model_dump()
    move_dict.pop("wait")
    pose = ArmPose(**move_dict)
    move_is_possible = controller.valid_pose(pose)
    if move_is_possible:
        return JSONResponse(content={"message": "Pose is valid"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Pose is not valid"}, status_code=400)

# --------
# Joints
# --------

@router.post("/joint/")
def move_joint(
    move: MoveJoint, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")

    joint_idx = move_dict.pop("joint_idx")
    joint_value = move_dict.pop("joint_value")
    controller.move_joint_to(joint_idx, joint_value)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


@router.post("/joint/relative/")
def move_joint_to_relative(
    move: MoveJoint, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")

    joint_idx = move_dict.pop("joint_idx")
    joint_value = move_dict.pop("joint_value")
    controller.move_joint_to_relative(joint_idx, joint_value)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


@router.post("/joints/relative/")
def move_joints_to_relative(
    move: MoveJoints, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")

    joint_values = move_dict.pop("joint_values")
    controller.move_joints_to_relative(joint_values)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


# --------
# Tool
# --------


@router.post("/tool/move/")
def tool_post(
    tool: Tool, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    tool_dict = tool.model_dump()
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

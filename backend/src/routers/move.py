from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from numpy import degrees
from pydantic import BaseModel
from robot_arm_controller.control.arm_kinematics import ArmPose
from robot_arm_controller.controller import ArmController
from robot_arm_controller.utils.algebra import degree2rad

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
    degrees: Optional[bool] = True


class Tool(BaseModel):
    toolValue: float
    wait: Optional[bool] = False
    degrees: Optional[bool] = True


class MoveJoint(BaseModel):
    joint_idx: int
    joint_value: float
    wait: Optional[bool] = False
    degrees: Optional[bool] = True


class HomeJoint(BaseModel):
    joint_idx: int
    wait: Optional[bool] = False


class MoveJoints(BaseModel):
    joint_values: list
    wait: Optional[bool] = False
    degrees: Optional[bool] = True


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
    degrees = move_dict.pop("degrees")

    pose = ArmPose(**move_dict, degree=degrees)

    move_is_possible = controller.move_to(pose)

    if wait:
        controller.wait_done_moving()
    if move_is_possible:
        return JSONResponse(content={"message": "Moved"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Not moved"}, status_code=400)


@router.post("/pose/relative/")
def move_relative(
    move: Move, controller: ArmController = controller_dependency
) -> JSONResponse:
    move_dict = move.model_dump()
    wait = move_dict.pop("wait")
    degrees = move_dict.pop("degrees")

    pose = ArmPose(**move_dict, degree=degrees)

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
    degrees = move_dict.pop("degrees")
    pose = ArmPose(**move_dict, degree=degrees)

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
    degrees = move_dict.pop("degrees")

    joint_idx = move_dict.pop("joint_idx")
    joint_value = move_dict.pop("joint_value")

    if degrees:
        joint_value = degree2rad(joint_value)

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
    degrees = move_dict.pop("degrees")

    joint_idx = move_dict.pop("joint_idx")
    joint_value = move_dict.pop("joint_value")
    if degrees:
        joint_value = degree2rad(joint_value)

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
    degrees = move_dict.pop("degrees")

    joint_values = move_dict.pop("joint_values")
    if degrees:
        joint_values = [degree2rad(joint_value) for joint_value in joint_values]

    controller.move_joints_to_relative(joint_values)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


# --------
# Tool
# --------


@router.post("/tool/")
def tool_post(
    tool: Tool, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    tool_dict = tool.model_dump()
    tool_value = tool_dict["toolValue"]
    wait = tool_dict["wait"]
    degrees = tool_dict["degrees"]
    if degrees:
        tool_value = degree2rad(tool_value)

    controller.set_tool_value(tool_value)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


@router.post("/tool/relative/")
def tool_relative(
    tool: Tool, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    tool_dict = tool.model_dump()
    tool_value = tool_dict["toolValue"]
    wait = tool_dict["wait"]
    degrees = tool_dict["degrees"]
    if degrees:
        tool_value = degree2rad(tool_value)

    print("\n\n\ntool_value", tool_value)
    controller.set_tool_value_relative(tool_value)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


@router.get("/tool/current/")
def tool_get(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    tool_value = controller.tool_value
    return {"toolValue": tool_value}

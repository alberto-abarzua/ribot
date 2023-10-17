from copy import deepcopy
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
    joint_idx = home_joint.dict().pop("joint_idx")
    controller.home_joint(joint_idx)
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


@router.post("/pose/validate/")
def valid_pose(
    move: Move, controller: ArmController = controller_dependency
) -> JSONResponse:
    move_dict = move.dict()
    move_dict.pop("wait")
    pose = ArmPose(**move_dict)
    move_is_possible = controller.valid_pose(pose)
    if move_is_possible:
        return JSONResponse(content={"message": "Pose is valid"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Pose is not valid"}, status_code=400)


@router.post("/joint/")
def move_joint(
    move: MoveJoint, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    move_dict = move.dict()
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
    move_dict = move.dict()
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
    move_dict = move.dict()
    wait = move_dict.pop("wait")

    joint_values = move_dict.pop("joint_values")
    controller.move_joints_to_relative(joint_values)
    if wait:
        controller.wait_done_moving()
    return {"message": "Moved"}


# --------
# Pose
# --------


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


# --------
# Status
# --------


@router.get("/status/")
def status(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    pose = controller.current_pose
    status_dict: Dict[str, Any] = deepcopy(pose.as_dict)
    status_dict["toolValue"] = controller.tool_value
    status_dict["isHomed"] = controller.is_homed
    status_dict["moveQueueSize"] = controller.move_queue_size
    status_dict["currentAngles"] = controller.current_angles
    return status_dict


@router.post("/stop/")
def stop_movement(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    controller.stop_movement()
    return {"message": "Movement stopped"}


# --------
# Angle
# --------

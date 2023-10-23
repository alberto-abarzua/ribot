from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from robot_arm_controller.controller import ArmController, Settings, ControllerStatus

from utils.general import controller_dependency

router = APIRouter()


class SetSetting(BaseModel):
    setting: int
    value: float
    joint_idx: Optional[int] = None


def get_items(
    setting: int,
    joint_idx: Optional[int],
    controller: ArmController = controller_dependency,
) -> Dict[Any, Any]:
    if joint_idx is not None:
        return {
            "setting": setting,
            "joint_idx": joint_idx,
            "value": controller.get_setting_joint(Settings(setting), joint_idx),
        }
    else:
        return {
            "setting": setting,
            "value": controller.get_setting_joints(Settings(setting)),
        }


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

    status_dict["connected"] = controller.status == ControllerStatus.RUNNING
    status_dict["status"] = controller.status
    return status_dict


@router.post("/stop/")
def stop_movement(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    controller.stop_movement()
    return {"message": "Movement stopped"}


@router.post("/health_check/")
def health_check(controller: ArmController = controller_dependency) -> Dict[Any, Any]:
    controller.health_check()
    return {"message": "Health check completed"}


# --------
# Settings
# --------


@router.post("/set/")
def set_item(
    item: SetSetting, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    item_dict = item.dict()
    setting = Settings(item_dict["setting"])
    value = item_dict["value"]
    joint_idx = item_dict["joint_idx"]
    if joint_idx is not None:
        controller.set_setting_joint(setting, value, joint_idx)

    controller.set_setting_joints(setting, value)

    return {"setting": setting, "value": value}


@router.post("/config_from_file/")
def config_from_file(
    file_path: str, controller: ArmController = controller_dependency
) -> Dict[Any, Any]:
    CONFIG_PATH = Path(__file__).parent.parent / "config"
    controller.configure_from_file(CONFIG_PATH / file_path)
    return {"config_from_file": file_path}


@router.get("/list_configs/")
def list_configs() -> Dict[Any, Any]:
    CONFIG_PATH = Path(__file__).parent.parent / "config"
    return {"configs": [str(f) for f in CONFIG_PATH.iterdir() if f.is_file()]}

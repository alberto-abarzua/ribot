from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from robot_arm_controller.controller import ArmController, Settings

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

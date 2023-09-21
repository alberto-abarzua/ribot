import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from robot_arm_controller.controller import Settings

from routers.move import router as move_router
from routers.settings import router as settings_router
from utils.general import get_controller

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(move_router, prefix="/move")
app.include_router(settings_router, prefix="/settings")


@app.on_event("startup")
async def startup_event() -> None:
    controller = get_controller()
    controller.start(wait=True)
    # controller.print_status = True
    controller.set_setting_joints(Settings.HOMING_OFFSET_RADS, np.pi / 4)
    controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 800)
    controller.set_setting_joints(Settings.CONVERSION_RATE_AXIS_JOINTS, 1.5)
    controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.4)
    offsets = controller.get_setting_joints(Settings.HOMING_OFFSET_RADS)
    print(offsets)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    controller = get_controller()
    controller.stop()

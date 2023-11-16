from typing import  Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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




# --------
# General
# --------


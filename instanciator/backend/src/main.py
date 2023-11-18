import os
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.instance_generator import InstanceGenerator

instance_generator = InstanceGenerator()

HOST = os.environ.get("HOST", "http://localhost")

ORIGIN = os.environ.get("ORIGIN", "http://localhost:3000")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/instances/")
async def get_instances() -> List[Dict[str, Any]]:
    instances = instance_generator.get_instances()
    return instances


@app.post("/instances/{uuid_str}/destroy")
async def destroy_instance(uuid_str: str) -> Dict[str, Any]:
    instance_generator.stop_by_uuid(uuid_str)
    return {"status": "ok"}


@app.post("/stop_all/")
async def destroy_all() -> Dict[str, Any]:
    instance_generator.stop_all()
    return {"status": "ok"}



@app.get("/backend_url/")
async def get_backend_port(request: Request, response: Response) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")
    instance = None
    instance_id = None

    if not instance_id_cookie:
        instance = instance_generator.create_instance()
        instance_id = instance.instance_uuid
        response.set_cookie(
            key="instance_id",
            value=instance_id,
            expires=30 * 60,
            httponly=True,
        )

    else:
        instance_id = instance_id_cookie
        instance = instance_generator.get_instance_by_uuid(instance_id)
        if not instance:
            instance = instance_generator.create_instance()
            instance_id = instance.instance_uuid
            response.set_cookie(
                key="instance_id",
                value=instance_id,
                expires=30 * 60,
                httponly=True,
            )
    ports = instance.get_ports()
    backend_port = ports.backend_http_port

    return {"backend_url": f"{HOST}:{backend_port}", "backend_port": backend_port, "host": HOST}


@app.get("/health_check/")
async def health_check(request: Request) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")

    if not instance_id_cookie:
        return {"status": "not found"}
    else:
        uuid = instance_id_cookie

    instance_generator.set_last_health_check(uuid)

    return {"status": "ok"}

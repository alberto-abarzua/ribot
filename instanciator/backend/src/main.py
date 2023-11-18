import os
import uuid
from typing import Any, Dict

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
async def get_instances() -> Dict[str, Any]:
    instances = instance_generator.get_instances()
    return instances


@app.get("/instances/{uuid_str}")
async def get_instance(uuid_str: str) -> Dict[str, Any]:
    instance = instance_generator.get_instance(uuid_str)
    if instance is None:
        return {"status": "not found"}
    else:
        return instance


@app.post("/instances/{uuid_str}/destroy")
async def destroy_instance(uuid_str: str) -> Dict[str, Any]:
    instance_generator.destroy(uuid_str)
    return {"status": "ok"}


@app.get("/instance/")
async def create_instance() -> Dict[str, Any]:
    new_uuid = uuid.uuid4().__str__()
    new_instance = instance_generator.create_instance(new_uuid)
    return new_instance


@app.post("/destroy_all/")
async def destroy_all() -> Dict[str, Any]:
    instance_generator.destroy_all()
    return {"status": "ok"}


@app.get("/backend_url/")
async def get_backend_port(request: Request, response: Response) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")

    if not instance_id_cookie:
        uuid = instance_generator.get_uuid()
        response.set_cookie(
            key="instance_id",
            value=uuid,
            expires=30 * 60,
            httponly=True,
        )
    else:
        uuid = instance_id_cookie

    instance = instance_generator.get_instance(uuid)
    if instance is None:
        new_uuid = instance_generator.get_uuid()
        response.set_cookie(
            key="instance_id",
            value=new_uuid,
            expires=30 * 60,
            httponly=True,
        )
        instance = instance_generator.get_instance(new_uuid)

    if instance is None:
        return {"status": "not found"}

    port = instance["ports"]["backend_http_port"]
    return {"backend_url": f"{HOST}:{port}", "backend_port": port, "host": HOST}


@app.get("/health_check/")
async def health_check(request: Request) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")

    if not instance_id_cookie:
        return {"status": "not found"}
    else:
        uuid = instance_id_cookie

    instance_generator.set_last_health_check(uuid)

    return {"status": "ok"}

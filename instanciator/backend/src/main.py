import os
from typing import Any, Dict, List

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.instance_generator import SingletonInstanceGenerator, InstanceGenerator


@asynccontextmanager
async def instance_generator_lifespan(_: FastAPI):  # type: ignore # noqa: ANN201
    instance_generator = SingletonInstanceGenerator.get_instance()

    yield

    instance_generator.stop()


HOST = os.environ.get("HOST", "http://localhost")

ORIGIN = os.environ.get("ORIGIN", "http://localhost:3000")


ACCESS_TOKENS = os.environ.get("ACCESS_TOKENS", "").split(",")


def verify_token(token: str):
    if token not in ACCESS_TOKENS:
        raise HTTPException(status_code=400, detail="Invalid token")
    return True


token_dependency = Depends(verify_token)
instanciator_dependency = Depends(SingletonInstanceGenerator.get_instance)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/instances/")
async def get_instances(instance_generator: InstanceGenerator = instanciator_dependency, _: str = token_dependency) -> List[Dict[str, Any]]:
    instances = instance_generator.get_instances()
    return instances


@app.post("/instances/{uuid_str}/destroy")
async def destroy_instance( uuid_str: str,instance_generator: InstanceGenerator = instanciator_dependency, _: str = token_dependency) -> Dict[str, Any]:
    instance_generator.stop_by_uuid(uuid_str)
    return {"status": "ok"}


@app.post("/stop_all/")
async def destroy_all(instance_generator: InstanceGenerator = instanciator_dependency, _: str = token_dependency) -> Dict[str, Any]:
    instance_generator.stop_all()
    return {"status": "ok"}


@app.get("/backend_url/")
async def get_backend_port(request: Request, response: Response, instance_generator: InstanceGenerator = instanciator_dependency, access_token: str = token_dependency) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")
    instance = None
    instance_id = None

    if not instance_id_cookie:
        instance = instance_generator.get_free_instance(access_token)
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
            instance = instance_generator.get_free_instance(access_token)
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
async def health_check(request: Request,instance_generator: InstanceGenerator = instanciator_dependency) -> Dict[str, Any]:
    instance_id_cookie = request.cookies.get("instance_id")

    if not instance_id_cookie:
        return {"status": "not found"}
    else:
        uuid = instance_id_cookie

    instance_generator.set_last_health_check(uuid)

    return {"status": "ok"}

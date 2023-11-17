
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from src.instance_generator import InstanceGenerator
import uuid
import os

instance_generator = InstanceGenerator()

HOST = os.environ.get('HOST', 'http://localhost')

ORIGIN = os.environ.get('ORIGIN', 'http://localhost:3000')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/instances/")
async def get_instances():
    instances = instance_generator.get_instances()
    return instances


@app.get("/instances/{uuid_str}")
async def get_instance(uuid_str: str):
    instance = instance_generator.get_instance(uuid_str)
    if instance is None:
        return None
    else:
        return instance




@app.post("/instances/{uuid_str}/destroy")
async def destroy_instance(uuid_str: str):
    instance_generator.destroy(uuid_str)
    return {"status": "ok"}

@app.get("/instance/")
async def create_instance():
    # generate a uuid
    new_uuid = uuid.uuid4().__str__()
    new_instance = instance_generator.get_or_create(new_uuid)
    return new_instance

@app.post('/destroy_all/')
async def destroy_all():
    instance_generator.destroy_all()
    return {"status": "ok"}


@app.get("/backend_url/")
async def get_backend_port(request: Request, response: Response):
    # Check if the cookie is set
    instance_id = request.cookies.get("instance_id")

    if instance_id:
        # Cookie exists, get or create the instance
        instance = instance_generator.get_or_create(instance_id)
    else:
        # Cookie does not exist, create a new instance
        new_uuid = str(uuid.uuid4())
        instance = instance_generator.get_or_create(new_uuid)

        # Set the cookie in the response and make it expire in 30 minutes
        response.set_cookie(
            key="instance_id",
            value=new_uuid,
            expires=30 * 60,
            httponly=True,
        )


    print(instance)
    port = instance['ports']['backend_http_port']
    host = HOST
    return {'backend_url': f'{host}:{port}'}


import json
import os
import socket
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import redis

PARENT_FILE_PATH = Path(__file__).parent


DOCKER_COMPOSE_FILE_PATH = (
    PARENT_FILE_PATH / "config" / "firmware-controller-compose.yaml"
)


class InstanceGenerator:
    def __init__(self) -> None:
        self.docker_compose_path = str(DOCKER_COMPOSE_FILE_PATH)
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0, decode_responses=True
        )
        self.start_instance_checker()

    def isntance_checker_target_fun(self) -> None:
        while True:
            instances = self.instances
            free_instances = 0

            for instance in instances.values():
                instance_uuid = instance["uuid"]

                if time.time() - instance["time_started"] > 30 * 60:
                    self.destroy(instance_uuid)
                    continue

                if instance["free"]:
                    free_instances += 1

            if free_instances <= 3:
                new_uuid = str(uuid.uuid4())
                new_instance = self.create_instance(new_uuid)
                new_instance["free"] = True
                instances[new_uuid] = new_instance

            self.instances = instances

            time.sleep(5)

    def start_instance_checker(self) -> None:
        thread = threading.Thread(target=self.isntance_checker_target_fun)
        thread.start()

    def get_instances(self) -> Dict[str, Any]:
        return self.instances

    @property
    def instances(self) -> Dict[str, Any]:
        json_str = self.redis_client.get("instances")
        if json_str is None:
            return {}
        else:
            return json.loads(str(json_str))

    @instances.setter
    def instances(self, value: Dict[str, Any]) -> None:
        self.redis_client.set("instances", json.dumps(value))

    def get_instance(self, uuid_str: str) -> Optional[Dict[str, Any]]:
        if uuid_str in self.instances:
            return self.instances[uuid_str]
        return None

    def get_free_port(self) -> int:
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", 0))  # Bind to port 0 to let the OS choose an available port
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                return port

    def get_project_name(self, uuid_str: str) -> str:
        return f"rtwin_instance_{uuid_str}"

    def get_uuid(self) -> str:
        instances = self.instances
        for instance in instances.values():
            if instance["free"]:
                instance["free"] = False
                return instance["uuid"]

        new_uuid = str(uuid.uuid4())
        new_instance = self.create_instance(new_uuid)
        new_instance["free"] = False
        instances[new_uuid] = new_instance
        self.instances = instances
        return new_uuid

    def create_instance(self, uuid_str: str) -> Dict[str, Any]:
        backend_http_port = self.get_free_port()
        controller_websocket_port = self.get_free_port()
        controller_server_port = self.get_free_port()

        env_vars = {
            "BACKEND_HTTP_PORT": str(backend_http_port),
            "CONTROLLER_WEBSOCKET_PORT": str(controller_websocket_port),
            "CONTROLLER_SERVER_PORT": str(controller_server_port),
            "ESP_CONTROLLER_SERVER_PORT": str(controller_server_port),
        }

        project_name = self.get_project_name(uuid_str)

        command = [
            "docker",
            "compose",
            "-f",
            self.docker_compose_path,
            "-p",
            project_name,
            "up",
            "-d",
        ]

        result = subprocess.check_call(command, env={**os.environ, **env_vars})
        if result != 0:
            raise Exception("docker compose failed")

        return {
            "ports": {
                "backend_http_port": backend_http_port,
                "controller_websocket_port": controller_websocket_port,
                "controller_server_port": controller_server_port,
            },
            "time_started": time.time(),
            "free": True,
            "uuid": uuid_str,
        }

    def destroy(self, uuid_str: str) -> None:
        if uuid_str in self.instances:
            project_name = self.get_project_name(uuid_str)
            instances = self.instances
            instance = instances[uuid_str]

            env_vars = {
                "BACKEND_HTTP_PORT": str(instance["ports"]["backend_http_port"]),
                "CONTROLLER_WEBSOCKET_PORT": str(
                    instance["ports"]["controller_websocket_port"]
                ),
                "CONTROLLER_SERVER_PORT": str(
                    instance["ports"]["controller_server_port"]
                ),
                "ESP_CONTROLLER_SERVER_PORT": str(
                    instance["ports"]["controller_server_port"]
                ),
            }
            command = [
                "docker",
                "compose",
                "-f",
                self.docker_compose_path,
                "-p",
                project_name,
                "down",
                "--remove-orphans",
            ]
            result = subprocess.check_call(command, env={**os.environ, **env_vars})
            if result != 0:
                raise Exception("docker ", "compose failed")
            instances = self.instances
            del instances[uuid_str]
            self.instances = instances

    def destroy_all(self) -> None:
        instances = self.instances
        for uuid_str in instances:
            self.destroy(uuid_str)

    def get_backend_port(self, uuid_str: str) -> Optional[int]:
        instances = self.instances
        port = None
        if uuid_str in instances:
            port = instances[uuid_str]["ports"]["backend_http_port"]

        return port

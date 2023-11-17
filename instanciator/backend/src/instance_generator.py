import socket
import threading
import subprocess
import os
import time
from pathlib import Path
import redis
import json
import random

PARENT_FILE_PATH = Path(__file__).parent


DOCKER_COMPOSE_FILE_PATH = PARENT_FILE_PATH / "firmware-controller-compose.yaml"


class InstanceGenerator:
    def __init__(self):
        self.docker_compose_path = str(DOCKER_COMPOSE_FILE_PATH)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.start_instance_checker()

    def get_instances(self):
        return self.instances

    @property
    def instances(self):
        json_str = self.redis_client.get('instances')
        if json_str is None:
            return {}
        else:
            return json.loads(str(json_str))

    @instances.setter
    def instances(self, value):
        self.redis_client.set('instances', json.dumps(value))

    def get_instance(self, uuid_str):
        if uuid_str in self.instances:
            return self.instances[uuid_str]
        else:
            return None

    def isntance_checker_target_fun(self):
        while True:
            for uuid_str in self.instances:
                instance = self.instances[uuid_str]
                if time.time() - instance['time_started'] > 30 * 60:
                    self.destroy(uuid_str)
            time.sleep(10)

    def start_instance_checker(self):
        thread = threading.Thread(target=self.isntance_checker_target_fun)
        thread.start()

    def get_free_port(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))  # Bind to port 0 to let the OS choose an available port
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                return port

    def get_project_name(self, uuid_str):
        return f"rtwin_instance_{uuid_str}"

    def get_or_create(self, uuid_str):
        instances = self.instances
        
        if uuid_str in instances:
            return instances[uuid_str]

        # Generate unique ports
        backend_http_port = self.get_free_port()
        controller_websocket_port = self.get_free_port()
        controller_server_port = self.get_free_port()

        # Set environment variables for Docker Compose
        env_vars = {
            "BACKEND_HTTP_PORT": str(backend_http_port),
            "CONTROLLER_WEBSOCKET_PORT": str(controller_websocket_port),
            "CONTROLLER_SERVER_PORT": str(controller_server_port),
            "ESP_CONTROLLER_SERVER_PORT": str(controller_server_port),
        }

        # Define the project name based on UUID
        project_name = self.get_project_name(uuid_str)

        # Launch Docker Compose
        # result = subprocess.run(
        #     ["docker-compose", "-f", self.docker_compose_path, "-p", project_name, "up", "-d"],
        #     env={**os.environ, **env_vars})

        command = ["docker-compose", "-f", self.docker_compose_path, "-p", project_name, "up", "-d"]

        result = subprocess.check_call(command, env={**os.environ, **env_vars})
        if result != 0:
            raise Exception("Docker Compose failed")

        # Store instance data
        instances[uuid_str] = {
            "ports": {
                "backend_http_port": backend_http_port,
                "controller_websocket_port": controller_websocket_port,
                "controller_server_port": controller_server_port
            },
            'time_started': time.time(),

        }


        self.instances = instances

        return instances[uuid_str]

    def destroy(self, uuid_str):
        if uuid_str in self.instances:
            project_name = self.get_project_name(uuid_str)
            isntances = self.instances
            instance = isntances[uuid_str]

            # get env variables
            env_vars = {
                "BACKEND_HTTP_PORT": str(instance['ports']['backend_http_port']),
                "CONTROLLER_WEBSOCKET_PORT": str(instance['ports']['controller_websocket_port']),
                "CONTROLLER_SERVER_PORT": str(instance['ports']['controller_server_port']),
                "ESP_CONTROLLER_SERVER_PORT": str(instance['ports']['controller_server_port']),
                    } 
            command = ["docker-compose", "-f", self.docker_compose_path, "-p", project_name, "down","--remove-orphans"]
            result = subprocess.check_call(command, env={**os.environ, **env_vars})
            if result != 0:
                raise Exception("Docker Compose failed")
            instances = self.instances
            del instances[uuid_str]
            self.instances = instances

    def destroy_all(self):
        instances = self.instances
        for uuid_str in instances:
            self.destroy(uuid_str)

    def get_backend_port(self, uuid_str):
        instances = self.instances
        port = None
        if uuid_str in instances:
            port = instances[uuid_str]['ports']['backend_http_port']
        return port

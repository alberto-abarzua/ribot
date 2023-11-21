import json
import os
import socket
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List
import dataclasses
import redis
import pickle
from threading import RLock, Event, Thread

PARENT_FILE_PATH = Path(__file__).parent


DOCKER_COMPOSE_FILE_PATH = (
    PARENT_FILE_PATH / "config" / "firmware-controller-compose.yaml"
)


@dataclasses.dataclass
class Ports:
    backend_http_port: int
    controller_websocket_port: int
    controller_server_port: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "backend_http_port": self.backend_http_port,
            "controller_websocket_port": self.controller_websocket_port,
            "controller_server_port": self.controller_server_port,
        }


class Instance:
    instance_uuid: str
    time_created: float
    free: bool = True
    ports: Ports
    time_last_health_check: Optional[float] = None
    access_token: Optional[str] = None

    def __init__(self):
        self.instance_uuid = str(uuid.uuid4())
        self.time_created = time.time()
        self.time_old_timout = 60 * 30
        self.time_old_health_check = 60 * 5
        self.time_last_health_check = None
        self.free = True
        self.access_token = None

        self.ports = Ports(
            backend_http_port=self.get_free_port(),
            controller_websocket_port=self.get_free_port(),
            controller_server_port=self.get_free_port(),
        )

    def get_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port = s.getsockname()[1]
            return port

    def get_ports(self) -> Ports:
        return self.ports

    def get_project_name(self) -> str:
        return f"rtwin_instance_{self.instance_uuid}"

    def get_env_vars(self) -> Dict[str, str]:
        return {
            "BACKEND_HTTP_PORT": str(self.ports.backend_http_port),
            "CONTROLLER_WEBSOCKET_PORT": str(self.ports.controller_websocket_port),
            "CONTROLLER_SERVER_PORT": str(self.ports.controller_server_port),
            "ESP_CONTROLLER_SERVER_PORT": str(self.ports.controller_server_port),
        }

    def health_check(self) -> bool:
        try:
            project_name = self.get_project_name()
            env_vars = self.get_env_vars()

            command = ["docker", "compose", "-f", DOCKER_COMPOSE_FILE_PATH,
                       '-p', project_name, "ps", "--format", "json"]

            result = subprocess.check_output(command, env={**os.environ, **env_vars})

            services = result.decode("utf-8").strip().split('\n')

            for service_str in services:
                try:
                    service = json.loads(service_str)
                    if service["State"] != "running":
                        return False
                except json.JSONDecodeError:

                    print(f"Error decoding JSON from service string: {service_str}")
                    return False

        except subprocess.CalledProcessError as e:
            print(f"Subprocess error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

        return True

    def set_last_health_check(self) -> None:
        self.time_last_health_check = time.time()

    def start(self) -> None:
        env_vars = self.get_env_vars()
        project_name = self.get_project_name()
        print(f"starting instance {project_name}")

        command = [
            "docker",
            "compose",
            "-f",
            DOCKER_COMPOSE_FILE_PATH,
            "-p",
            project_name,
            "up",
            "-d",
        ]

        result = subprocess.check_call(command, env={**os.environ, **env_vars})
        if result != 0:
            raise Exception("docker compose failed")

    def stop(self) -> None:
        env_vars = self.get_env_vars()
        project_name = self.get_project_name()
        print(f"stopping {project_name}")

        command = [
            "docker",
            "compose",
            "-f",
            DOCKER_COMPOSE_FILE_PATH,
            "-p",
            project_name,
            "down",
            "--remove-orphans",
        ]

        result = subprocess.check_call(command, env={**os.environ, **env_vars})
        if result != 0:
            raise Exception("docker compose failed")

    def should_stop(self) -> bool:
        old = False
        healthy = self.health_check()
        old_health_check = self.time_last_health_check is not None and time.time(
        ) - self.time_last_health_check > 60 * 5
        return old or old_health_check or not healthy

    def as_dict(self) -> Dict[str, Any]:
        return {
            "instance_uuid": self.instance_uuid,
            "time_created": self.time_created,
            "free": self.free,
            "ports": self.ports,
            "time_last_health_check": self.time_last_health_check,
            "readable_time_last_health_check": time.ctime(self.time_last_health_check) if self.time_last_health_check is not None else "None",
            "healthy": self.health_check(),
            "access_token": self.access_token
        }


class InstanceGenerator:
    instances: list[Instance]

    def __init__(self) -> None:
        self.docker_compose_path = str(DOCKER_COMPOSE_FILE_PATH)
        self.redis_client = redis.Redis(
            host="localhost", port=6379, db=0
        )

        self.instances_lock = RLock()
        self.stop_event = Event()
        self.instances = []
        self.min_instances = int(os.environ.get("MIN_INSTANCES", 10))
        self.max_instances = int(os.environ.get("MAX_INSTANCES", 20))
        self.check_interval = 20
        self.prune_interval = 60 * 60
        self.threads = []
        self.start_instance_checker()

    @staticmethod
    def redis_instances(func):
        def wrapper(self, *args, **kwargs):
            try:
                with self.instances_lock:
                    redis_object = self.redis_client.get("instances")
                    if redis_object is not None:
                        self.instances = pickle.loads(redis_object)
                    else:
                        self.instances = []

                    result = func(self, *args, **kwargs)

                    pickled_instances = pickle.dumps(self.instances)
                    self.redis_client.set("instances", pickled_instances)
                    return result

            except (redis.RedisError, pickle.PickleError) as error:
                print(f"An error occurred: {error}")
                raise
        return wrapper

    def start_instance_checker(self) -> None:
        instance_checker_thread = Thread(target=self.instance_checker_target_fun)
        instance_checker_thread.start()

        prune_thread = Thread(target=self.prune_target_fun)
        prune_thread.start()

        self.threads.append(instance_checker_thread)
        self.threads.append(prune_thread)

    @redis_instances
    def instance_checker_target_fun(self) -> None:
        while not self.stop_event.wait(self.check_interval):
            try:
                print("checking instances")
                for instance in self.instances:
                    if instance.should_stop():
                        instance.stop()
                        self.instances.remove(instance)

                num_instances = len(self.instances)
                if num_instances > self.max_instances:
                    free_instances = [instance for instance in self.instances if instance.free]
                    if len(free_instances) == 0:
                        print("no free instances, can't stop")
                        oldest_instance = self.instances[-1]
                    else:
                        oldest_instance = min(free_instances, key=lambda instance: instance.time_created)

                    oldest_instance.stop()
                    self.instances.remove(oldest_instance)

                num_free = sum(1 for instance in self.instances if instance.free)

                if num_free < self.min_instances and num_instances < self.max_instances:
                    print("creating new instance")
                    self.create_instance()

            except Exception as e:
                print(f"Unexpected error: {e}")

    def prune_target_fun(self) -> None:
        while not self.stop_event.wait(self.prune_interval):
            self.prune()

    def prune(self) -> None:
        command = ["docker", "system", "prune", "-f"]
        try:
            subprocess.check_call(command)
        except subprocess.CalledProcessError:
            pass

    @redis_instances
    def get_free_instance(self, access_token: str) -> Instance:
        for instance in self.instances:
            if instance.free:
                instance.free = False
                instance.access_token = access_token
                instance.set_last_health_check()
                return instance

        new_instance = self.create_instance()
        new_instance.access_token = access_token
        new_instance.free = False
        return new_instance

    @redis_instances
    def create_instance(self) -> Instance:
        instance = Instance()
        instance.start()
        self.instances.append(instance)
        return instance

    @redis_instances
    def get_instance_by_uuid(self, instance_uuid: str) -> Optional[Instance]:
        for instance in self.instances:
            if instance.instance_uuid == instance_uuid:
                return instance
        return None

    @redis_instances
    def stop_all(self) -> None:
        for instance in self.instances:
            instance.stop()
            self.instances.remove(instance)

    @redis_instances
    def stop_by_uuid(self, instance_uuid: str) -> None:
        instance = self.get_instance_by_uuid(instance_uuid)
        if instance is not None:
            instance.stop()
            self.instances.remove(instance)

    @redis_instances
    def get_instances(self) -> List[Dict[str, Any]]:
        return [instance.as_dict() for instance in self.instances]

    @redis_instances
    def set_last_health_check(self, instance_uuid: str) -> None:
        instance = self.get_instance_by_uuid(instance_uuid)
        if instance is not None:
            instance.set_last_health_check()

    def stop(self) -> None:
        self.stop_event.set()
        for thread in self.threads:
            thread.join()


class SingletonInstanceGenerator:
    instance: Optional[InstanceGenerator] = None

    @staticmethod
    def get_instance() -> InstanceGenerator:
        if SingletonInstanceGenerator.instance is None:
            SingletonInstanceGenerator.instance = InstanceGenerator()
        return SingletonInstanceGenerator.instance

#!/usr/bin/env python3

from logging import captureWarnings
from sys import stdout
import time
import argparse
import subprocess
import re
import os
import signal
import socket
import toml
from typing import List
from pathlib import Path
import serial.tools.list_ports
from concurrent.futures import ThreadPoolExecutor

CURRENT_FILE_PATH = Path(__file__).parent.absolute()
DOCKER_SERVICES = CURRENT_FILE_PATH/'docker_services'


# ========================
#  Manger for docker compose
# ========================

class DockerService:

    def __init__(self, file_path: Path) -> None:

        self.file_path = file_path

    @property
    def name(self) -> str:
        return self.file_path.name.split('.')[0]

    @property
    def file_name(self) -> str:
        return self.file_path.name

    @property
    def full_path(self) -> str:
        return str(self.file_path.absolute())

    def get_dash_f(self) -> List[str]:
        return ['-f', self.full_path]


class DockerManger:

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.services: List[DockerService] = self.get_services()

    def get_services(self):
        services = []
        for file in self.base_path.iterdir():
            file = Path(file)
            if file.is_file() and file.name.endswith('.yaml') or file.name.endswith('.yml'):
                services.append(DockerService(file))
        return services

    def get_service_from_name(self, name: str) -> DockerService:
        if name.endswith('.yaml') or name.endswith('.yml'):
            name = name.split('.')[0]
        for service in self.services:
            if service.name == name:
                return service
        raise Exception(f"Service {name} not found")

    def get_file_list(self, services: List[str]) -> List[str]:
        file_list = []

        for service in services:
            file_list.extend(['-f', self.get_service_from_name(service).full_path])
        return file_list

    def dc_run(self, service_name: str, command: str, env={}, service_ports_and_aliases=False, exec=False):
        command_list = command.split(' ')
        service = self.get_service_from_name(service_name)

        new_command = ['docker', 'compose'] + service.get_dash_f()

        if exec:
            new_command.append('exec')
        else:
            new_command.extend(['run', '--rm'])
        if service_ports_and_aliases:
            new_command.extend(['--service-ports', '--use-aliases'])

        new_command.extend(command_list)

        result = subprocess.run(new_command, env={**os.environ, **env})
        # repalce with os.system to get output
        # result = os.system(' '.join(new_command))

        return result.returncode

    def dc_up(self, files: List[str], env: dict = {}, detached=False):

        file_list = self.get_file_list(files)
        command = ['docker', 'compose', *file_list, 'up']
        if detached:
            command.append('-d')
        return subprocess.check_call(command, env={**os.environ, **env})

    def dc_down(self, files: List[str]):
        file_list = self.get_file_list(files)
        return subprocess.check_call(['docker', 'compose', *file_list, 'down', '--remove-orphans'])

    def dc_build(self, files: List[str], no_cache=False):
        file_list = self.get_file_list(files)
        command = ['docker', 'compose', *file_list, 'build']
        if no_cache:
            command.append('--no-cache')
        return subprocess.check_call(command, env={**os.environ})

    def dc_logs(self, files: List[str]):
        file_list = self.get_file_list(files)
        return subprocess.check_call(['docker', 'compose', *file_list, 'logs', '--follow'])

    def dc_command(self, files: List[str], command: str):
        file_list = self.get_file_list(files)
        command_list = []

        if "run" in command:
            command_list += ["run", "--service-ports", "--use-aliases"]
            command_list += command.split(' ')[1:]
        else:
            command_list += command.split(' ')
        return subprocess.check_call(['docker', 'compose', *file_list] + command_list, env={**os.environ})


class Manager:

    def __init__(self):
        self.docker_manager = DockerManger(DOCKER_SERVICES)
        self.serivice_names = [service.name for service in self.docker_manager.services]

        self.current_host_ip = self.get_ip()

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"Error obtaining IP address: {e}")
            exit(1)

    def source_settings(self, file_path):
        with open(file_path, 'r') as f:
            settings = toml.load(f)
            for field, value_dict in settings.items():
                for sub_key, value in value_dict.items():
                    if "no_pref" in field.lower():
                        os.environ[sub_key.upper()] = str(value)
                    else:
                        os.environ[f"{field}_{sub_key}".upper()] = str(value)

    def source_env(self, file_path):
        pattern = re.compile(r'^(?:export\s+)?([\w\.]+)\s*=\s*(.*)$')
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                match = pattern.match(line)
                if match:
                    key, value = match.groups()
                    value = value.strip('\'"')
                    os.environ[key] = value

    def build_firmware(self, **kwargs):
        locally = kwargs.get('locally', False)
        if locally:
            self.build_firmware_locally()
        else:
            self.docker_manager.dc_run('firmware.yaml', 'firmware build')

    def build_firmware_locally(self, **_):
        subprocess.check_call(['rm', '-rf', 'build'], cwd='firmware')
        subprocess.check_call(['cmake', '-DCMAKE_EXPORT_COMPILE_COMMANDS=1', '.'],
                              cwd='firmware')
        subprocess.check_call(['cmake', '--build', '.', '--clean-first'],
                              cwd='firmware')
        subprocess.check_call(['make'], cwd='firmware')

    def down(self, **kwargs):
        container_name = kwargs.get('container', None)
        if container_name is not None:
            self.docker_manager.dc_down([container_name])
        else:
            self.docker_manager.dc_down(self.serivice_names)

    def up(self, **kwargs):
        container_name = kwargs.get('container', None)
        if container_name is not None:
            self.docker_manager.dc_up([container_name])

    def build(self, **kwargs):
        container_name = kwargs.get('container', None)
        no_editable = kwargs.get('no_editable', False)
        no_cache = kwargs.get('no_cache', False)
        os.environ['BACKEND_EDITABLE_PACKAGES'] = 'true' if not no_editable else 'false'
        try:
            subprocess.check_call(['rm', '-rf', 'controller'], cwd='backend')
            subprocess.check_call(['cp', '-r', '../controller', '.'], cwd='backend')

            if container_name is not None:
                self.docker_manager.dc_build([container_name], no_cache=no_cache)
            else:
                self.docker_manager.dc_build(self.serivice_names, no_cache=no_cache)

        finally:
            subprocess.check_call(['rm', '-rf', 'controller'], cwd='backend')

    def get_usb_port(self):
        ports = serial.tools.list_ports.comports()
        print("Available ports:")

        for port in ports:
            print(f"{port.device} - {port.description}")
            if 'CP210' in port.description or 'FTDI' in port.description or 'CH340' in port.description:
                return port.device
        return None

    def dc_command(self, **kwargs):
        container_name = kwargs.get('container', None)
        command = kwargs.get('op', None)
        if container_name is not None:
            self.docker_manager.dc_command([container_name], command)
        else:
            self.docker_manager.dc_command(self.serivice_names, command)

    def build_flash_esp(self, **kwargs):
        usb_port = kwargs.get('usb_port', None)

        if usb_port is None:
            usb_port = self.get_usb_port()
            print(usb_port)
            if usb_port is None:
                print("No ESP32 found")
                exit(1)

        os.environ['ESP_CONTROLLER_SERVER_HOST'] = self.current_host_ip

        print(f"Flashing ESP32 on port {usb_port}")

        process = None
        try:
            command_server = ['esp_rfc2217_server.py', '-p', '4000', usb_port]

            # run in background but still keep output
            process = subprocess.Popen(command_server)

            time.sleep(2)

            if process.poll() is not None:
                print("Error starting ESP32 server")
                exit(1)

            print("Waiting for ESP32 to connect...")

            self.docker_manager.dc_run(
                'esp_idf.yaml', 'esp_idf idf.py build flash -p rfc2217://host.docker.internal:4000?ign_set_control monitor')

        finally:
            if process:
                # send sigint to stop server
                process.send_signal(signal.SIGINT)

    def build_esp_locally(self, **kwargs):
        print("Requires idf.py to be installed and environment variables to be set")
        print("Also requires to export variables from .env file -->\n\t source .env")
        if 'IDF_PATH' not in os.environ:
            print("IDF_PATH is not set")
            exit(1)

        flash = kwargs.get('flash', False)

        delete_command = ['rm', '-rf', 'build', 'CMakeFiles', 'CMakeCache.txt',
                          'cmake_install.cmake', 'Makefile', 'compile_commands.json']
        subprocess.check_call(delete_command, cwd='firmware')

        command = ['idf.py', 'build']
        if flash:
            command.append('flash')

        subprocess.check_call(['rm', '-rf', 'build'], cwd='firmware')
        subprocess.check_call(command,
                              cwd='firmware', env=os.environ)

    def publish_controller(self, **kwargs):
        if 'CONTROLLER_PDM_PUBLISH_USERNAME' not in os.environ:
            print("CONTROLLER_PDM_PUBLISH_USERNAME is not set")
            exit(1)

        if 'CONTROLLER_PDM_PUBLISH_PASSWORD' not in os.environ:
            print("CONTROLLER_PDM_PUBLISH_PASSWORD is not set")
            exit(1)

        version = kwargs.get('version', None)

        if version is not None:
            os.environ['CONTROLLER_PDM_OVERRIDE_VERSION'] = version

        else:
            os.environ['CONTROLLER_PDM_INCREMENT_VERSION'] = 'true'

        self.docker_manager.dc_run('controller.yaml', 'controller pdm publish')

    def build_esp(self, **kwargs):

        flash = kwargs.get('flash', False)
        locally = kwargs.get('locally', False)
        ssid = kwargs.get('ssid', None)
        password = kwargs.get('password', None)
        controller_host = kwargs.get('controller_host', None)

        if ssid is not None:
            os.environ['ESP_WIFI_SSID'] = ssid

        if password is not None:
            os.environ['ESP_WIFI_PASSWORD'] = password

        os.environ['ESP_CONTROLLER_SERVER_HOST'] = self.current_host_ip

        if controller_host is not None:
            os.environ['ESP_CONTROLLER_SERVER_HOST'] = controller_host

        os.environ['VERBOSE'] = '1'

        if locally:
            self.build_esp_locally(**kwargs)

        else:
            if flash:
                self.build_flash_esp(**kwargs)

            else:
                self.docker_manager.dc_run('esp_idf.yaml', 'esp_idf idf.py build')

    def run_command(self, args):
        container, cmd = args
        try:
            self.docker_manager.dc_run(container, cmd, service_ports_and_aliases=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")

    def format_code(self, **kwargs):
        container_name = kwargs.get('container', None)

        if container_name is None:
            commands = [
                ('firmware.yaml', 'firmware format'),
                ('controller.yaml', 'controller pdm run format'),
                ('backend.yaml', 'backend pdm run format'),
                ('frontend.yaml', 'frontend npm run format')
            ]
            with ThreadPoolExecutor(max_workers=len(commands)) as executor:

                futures = []
                for cmd in commands:
                    print('Formatting', cmd[0])
                    time.sleep(0.4)
                    futures.append(executor.submit(self.run_command, cmd))
                for future in futures:
                    future.result()
            return
        if 'firmware' in container_name:
            self.docker_manager.dc_run('firmware.yaml', 'firmware format')
            return

        if 'controller' in container_name:
            self.docker_manager.dc_run('controller.yaml', 'controller pdm run format')
            return

        if 'backend' in container_name:
            self.docker_manager.dc_run('backend.yaml', 'backend pdm run format')
            return

        if 'frontend' in container_name:
            self.docker_manager.dc_run('frontend.yaml', 'frontend npm run format')
            return

    def lint(self, **kwargs):
        container_name = kwargs.get('container', None)

        if container_name is None:

            commands = [
                ('controller.yaml', 'controller pdm run lint'),
                ('backend.yaml', 'backend pdm run lint'),
                ('frontend.yaml', 'frontend npm run lint')
            ]
            with ThreadPoolExecutor(max_workers=len(commands)) as executor:

                futures = []
                for cmd in commands:
                    print('Linting', cmd[0])
                    time.sleep(1)
                    futures.append(executor.submit(self.run_command, cmd))
                for future in futures:
                    future.result()
            return

        if 'frontend' in container_name:
            self.docker_manager.dc_run('frontend.yaml', 'frontend npm run lint')
            return

        if 'controller' in container_name:
            self.docker_manager.dc_run('controller.yaml', 'controller pdm run lint')
            return

        if 'backend' in container_name:
            self.docker_manager.dc_run('backend.yaml', 'backend pdm run lint')
            return

    def test_debug(self, **_):
        os.environ["CONTROLLER_PRINT_STATUS"] = "true"

        self.docker_manager.dc_up(['controller.yaml', 'firmware.yaml'], env={
            "ESP_CONTROLLER_SERVER_HOST": "controller", "CONTROLLER_COMMAND": "test"})
        self.docker_manager.dc_down(['controller.yaml', 'firmware.yaml'])

    def test_no_debug(self, **_):
        self.build_firmware()
        self.docker_manager.dc_up(['firmware.yaml'], env={
            "ESP_CONTROLLER_SERVER_HOST": "controller"}, detached=True)

        exit_code = self.docker_manager.dc_run('controller.yaml', 'controller pdm run test',
                                               service_ports_and_aliases=True)

        print(exit_code)

        self.docker_manager.dc_down(['firmware.yaml'])
        if exit_code == 0:
            print("Tests passed")
            exit(0)
        else:
            print("Tests failed")

            exit(1)

    def test_esp(self, **_):
        exit_code = self.docker_manager.dc_run('controller.yaml', 'controller pdm run test',
                                               service_ports_and_aliases=True)
        if exit_code == 0:
            print("Tests passed")
            exit(0)
        else:
            print("Tests failed")
            exit(1)

    def test(self, **kwargs):
        debug = kwargs['debug']
        esp = kwargs['esp']
        if esp:
            self.test_esp(**kwargs)
            return
        if debug:
            self.test_debug(**kwargs)
        else:
            self.test_no_debug(**kwargs)

    def runserver(self, **kwargs):
        esp = kwargs.get('esp', False)
        detached = kwargs.get('detached', False)
        use_instanciator = kwargs.get('use_instanciator', False)
        if use_instanciator:
            os.environ['VITE_BACKEND_URL'] = 'no_backend'
            service_list = ['frontend.yaml']
        else:

            service_list = ['backend.yaml', 'unity_webgl_server.yaml', 'frontend.yaml']

        if not esp and not use_instanciator:
            service_list.append('firmware.yaml')

        if esp:
            os.environ["ESP_CONTROLLER_SERVER_HOST"] = self.current_host_ip

        self.docker_manager.dc_up(service_list, detached=detached)

        if not detached:
            self.docker_manager.dc_down(service_list)

    def shell(self, **kwargs):
        container_name = kwargs['container']
        self.docker_manager.dc_run(container_name, f'{container_name} /bin/sh', exec=False)

    def handle_sigint(self, signum, frame):
        self.down()
        print("Containers stopped. Exiting...")
        exit(0)

    def parse_and_execute(self):

        try:
            self.source_env(".env")
        except FileNotFoundError:
            self.source_settings("settings.toml")

        try:
            self.source_settings("secrets.toml")
        except FileNotFoundError:
            print("No secrets.toml file found. Continuing without secrets")

        signal.signal(signal.SIGINT, self.handle_sigint)
        parser = argparse.ArgumentParser(
            description='Robot arm manager.',
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(dest='command')
        # --------------
        # Docker compose command
        # --------------

        parser_dc = subparsers.add_parser(
            'docker-compose', help='Run docker compose command')

        parser_dc.set_defaults(func=self.dc_command)

        parser_dc.add_argument(
            '--op', help='Command to run')

        parser_dc.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to run command in')

        # --------------
        # Build firmware
        # --------------

        parser_buildf = subparsers.add_parser(
            'buildf', help='Build the firmware for linux platform')
        parser_buildf.set_defaults(func=self.build_firmware)

        parser_buildf.add_argument(
            '--locally', '-l', action='store_true', help='Build firmware locally')

        # --------------
        # Build docker compose
        # --------------

        parser_build = subparsers.add_parser(
            'build', help='Build all docker compose services')

        parser_build.set_defaults(func=self.build)

        parser_build.add_argument(
            '--no-cache', action='store_true', help='Build all docker compose services without cache')
        parser_build.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to build')

        parser_build.add_argument(
            '--no-editable', action='store_true', help='Build all docker compose services without editable mode')

        # --------------
        # Build esp
        # --------------

        parser_build_esp = subparsers.add_parser(
            'build-esp', help='Build the firmware for esp32 platform')

        parser_build_esp.set_defaults(func=self.build_esp)

        parser_build_esp.add_argument(
            '--locally', '-l', action='store_true', help='Build firmware locally')

        parser_build_esp.add_argument(
            '--usb-port', '-u', help='USB port for esp32')

        parser_build_esp.add_argument(
            '--flash', '-f', action='store_true', help='Build and flash firmware to esp32')

        parser_build_esp.add_argument(
            '--ssid', help='SSID for wifi')
        parser_build_esp.add_argument(
            '--password', help='Password for wifi')

        parser_build_esp.add_argument(
            '--controller-host', help='Host for controller')

        # --------------
        # Format code
        # --------------

        parser_format = subparsers.add_parser(
            'format', help='Format all code')

        parser_format.set_defaults(func=self.format_code)

        parser_format.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to format')

        # --------------
        # Lint code
        # --------------

        parser_lint = subparsers.add_parser('lint', help='Lint all code')

        parser_lint.set_defaults(func=self.lint)

        parser_lint.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to lint')

        # --------------
        # Test code
        # --------------

        parser_test = subparsers.add_parser('test', help='Run all tests')

        parser_test.set_defaults(func=self.test)

        parser_test.add_argument(
            '--debug', action='store_true', help='Run tests in debug mode')

        parser_test.add_argument(
            '--esp', action='store_true', help='Run tests on esp32')

        # --------------
        # Run server
        # --------------

        parser_runserver = subparsers.add_parser(
            'runserver', help='Run server')

        parser_runserver.set_defaults(func=self.runserver)

        parser_runserver.add_argument(
            '--esp', action='store_true', help='Run server for ESP-32 ')
        parser_runserver.add_argument(
            '--detached', '-d', action='store_true', help='Run server in detached mode')

        parser_runserver.add_argument(
            '--use-instanciator', action='store_true', help='Run server with instanciator')

        # --------------
        #  Publish controller
        # --------------

        parser_publish_controller = subparsers.add_parser(
            'publish-controller', help='Publish controller to PyPi')

        parser_publish_controller.set_defaults(func=self.publish_controller)

        parser_publish_controller.add_argument(
            '--version', '-v', help='Version to publish')

        # --------------
        # Stop containers
        # --------------

        parser_down = subparsers.add_parser(
            'down', help='Stop all containers')

        parser_down.set_defaults(func=self.down)

        parser_down.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to stop')

        # --------------
        # Shell
        # --------------

        parser_shell = subparsers.add_parser(
            'shell', help='Run shell in container')

        parser_shell.set_defaults(func=self.shell)

        parser_shell.add_argument(
            'container', choices=self.serivice_names, help='Container to run shell in')

        # ------------
        # Up
        # ------------

        parser_up = subparsers.add_parser(
            'up', help='Start certain container')

        parser_up.set_defaults(func=self.up)

        parser_up.add_argument(
            '--container', '-c', choices=self.serivice_names, help='Container to start')

        parsed_args, remaining_args = parser.parse_known_args()
        command_map = {
            'build': self.build,
            'buildf': self.build_firmware,
            'build-esp': self.build_esp,
            'format': self.format_code,
            'lint': self.lint,
            'up': self.up,
            'test': self.test,
            'runserver': self.runserver,
            'down': self.down,
            'shell': self.shell,
            'publish-controller': self.publish_controller,
            'docker-compose': self.dc_command

        }

        if parsed_args.command is None:
            parser.print_help()
            exit(1)

        command_map[parsed_args.command](**vars(parsed_args))


if __name__ == "__main__":
    manager = Manager()
    manager.parse_and_execute()

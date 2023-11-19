#!/usr/bin/env python3

import argparse
import os
import re
import subprocess

from pathlib import Path

SYSTEMD_SERVICE_TEMPLATE = """
[Unit]
Description=Instanciator service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/env python3 {script_command}
WorkingDirectory={working_directory}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""


CURRENT_FILE_PATH = Path(__file__).parent


class Deploy:

    def source_env(self, file_path):
        pattern = re.compile(r'^(?:export\s+)?([\w\.]+)\s*=\s*(.*)$')

        try:
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
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")
        except Exception as e:
            print(f"An error occurred while processing the environment file: {e}")

    def create_systemd_service(self):
        script_command = f"{CURRENT_FILE_PATH}/deploy.py start"

        service_content = SYSTEMD_SERVICE_TEMPLATE.format(script_command,
                                                          working_directory=str(CURRENT_FILE_PATH)
                                                          )

        service_file_path = '/etc/systemd/system/instanciator.service'

        with open(service_file_path, 'w') as file:
            file.write(service_content)

        subprocess.run(['systemctl', 'daemon-reload'])
        subprocess.run(['systemctl', 'enable', 'mycustomservice'])
        subprocess.run(['systemctl', 'start', 'mycustomservice'])

    def parse_and_execute(self):
        parser = argparse.ArgumentParser(description='Deploy services')
        parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'])
        self.source_env(CURRENT_FILE_PATH / '.env')

        args = parser.parse_args()

        if args.action == 'start':
            subprocess.run(['docker', 'compose', 'up', '-d'])
            subprocess.check_call(['pdm', 'run', 'start'], env=os.environ, cwd='backend')
        elif args.action == 'setup':
            subprocess.run(['docker', 'compose', 'up', '-d'])
            subprocess.check_call(['pdm', 'install'], env=os.environ, cwd='backend')

        elif args.action == 'stop':
            subprocess.run(['docker', 'compose', 'down', '--remove-orphans'])


if __name__ == "__main__":
    manager = Deploy()
    manager.parse_and_execute()

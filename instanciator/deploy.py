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
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin"
ExecStart={script_command}
WorkingDirectory={working_directory}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
SYSTEMD_TIMER_TEMPLATE = """
[Unit]
Description=Instanciator timer

[Timer]
[Timer]
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
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

        service_content = SYSTEMD_SERVICE_TEMPLATE.format(script_command=script_command,
                                                          working_directory=str(CURRENT_FILE_PATH)
                                                          )

        service_file_path = '/etc/systemd/system/instanciator.service'

        with open(service_file_path, 'w') as file:
            file.write(service_content)

        timer_file_path = '/etc/systemd/system/instanciator.timer'

        with open(timer_file_path, 'w') as file:
            file.write(SYSTEMD_TIMER_TEMPLATE)

        subprocess.run(['systemctl', 'daemon-reload'])
        subprocess.run(['systemctl', 'enable', 'instanciator.timer'])
        subprocess.run(['systemctl', 'start', 'instanciator.timer'])
        subprocess.run(['systemctl', 'enable', 'instanciator'])
        subprocess.run(['systemctl', 'start', 'instanciator'])

    def parse_and_execute(self):
        parser = argparse.ArgumentParser(description='Deploy services')
        parser.add_argument('action', choices=['start', 'stop', 'setup', 'status'])
        self.source_env(CURRENT_FILE_PATH / '.env')

        args = parser.parse_args()

        if args.action == 'start':
            subprocess.run(['docker', 'compose', 'up', '-d'])
            subprocess.check_call(['pdm', 'run', 'start'], env=os.environ, cwd='backend')
        elif args.action == 'setup':
            self.create_systemd_service()
        elif args.action == 'stop':
            subprocess.run(['docker', 'compose', 'down', '--remove-orphans'])

        elif args.action == 'status':
            subprocess.run(['docker', 'compose', 'ps'])
            subprocess.run(['systemctl', 'status', 'instanciator.service'])


if __name__ == "__main__":
    manager = Deploy()
    manager.parse_and_execute()

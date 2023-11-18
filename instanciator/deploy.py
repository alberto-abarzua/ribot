#!/usr/bin/env python3

import argparse
import os
import re
import subprocess


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

    def parse_and_execute(self):
        parser = argparse.ArgumentParser(description='Deploy services')
        parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'])

        args = parser.parse_args()

        if args.action == 'start':
            subprocess.run(['docker', 'compose', 'up', '-d'])
            subprocess.check_call(['pdm', 'run', 'start'])

        elif args.action == 'stop':
            subprocess.run(['docker', 'compose', 'down', '--remove-orphans'])


if __name__ == "__main__":
    manager = Deploy()
    manager.parse_and_execute()

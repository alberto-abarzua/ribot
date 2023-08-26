#!/usr/bin/env python3

import argparse
import subprocess
import os
import time
import signal


def get_ip(**kwargs):
    return subprocess.getoutput("hostname -I | awk '{print $1}'").strip()

def source_env(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            key, value = line.split('=', 1)
            os.environ[key] = value




def build_firmware(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'firmware', 'build'])

def down(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'down', '--remove-orphans'])
    
def build(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'build'])
    
def build_esp(**kwargs):
    os.environ['CONTROLLER_SERVER_HOST'] = get_ip()
    subprocess.check_call(['./firmware/entrypoint_esp.sh'])


def format_code(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'firmware', 'format'])
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'controller', 'pdm', 'run', 'format'])
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'backend', 'pdm', 'run', 'format'])
    
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'frontend', 'npm','run','format'])
    


def lint(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'controller', 'pdm', 'run', 'lint'])
    
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'backend', 'pdm', 'run', 'lint'])
    
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'frontend', 'npm','run','lint'])

def test(**kwargs):
    build_firmware()
    subprocess.check_call(['docker', 'compose', 'up', 'firmware', '-d'],
                          env={'ESP_CONTROLLER_SERVER_HOST': 'controller'})
    start_timestamp = int(time.time())
    while "Hardware setup complete" not in subprocess.getoutput('docker compose logs firmware'):
        time.sleep(1)
        if int(time.time()) - start_timestamp > 120:
            print("Firmware failed to start")
            subprocess.check_call(['docker', 'compose', 'logs', 'firmware'])
            subprocess.check_call(
                ['docker', 'compose', 'down', '--remove-orphans'])
            exit(1)
    time.sleep(5)
    subprocess.check_call(['docker', 'compose', 'logs', 'firmware'])
    print("Firmware is ready")
    os.environ['CONTROLLER_SERVER_HOST'] = 'controller'
    exit_code = subprocess.call(['docker', 'compose', 'run', '--rm', '--service-ports', '--use-aliases',
                                'controller', 'pdm', 'run', 'test'])
    if exit_code == 0:
        print("Tests passed")
    else:
        print("Tests failed")
        subprocess.check_call(['docker', 'compose', 'logs', 'firmware'])
    subprocess.check_call(['docker', 'compose', 'down', '--remove-orphans'])
    exit(exit_code)

def build_flash_esp(**kwargs):
    os.environ['ESP_CONTROLLER_SERVER_HOST'] = get_ip()
    print("Requires idf.py to be installed and environment variables to be set")
    print("Also requires to export variables from .env file -->\n\t source .env")
    if 'IDF_PATH' not in os.environ:
        print("IDF_PATH is not set")
        exit(1)

    subprocess.check_call(['rm', '-rf', 'build'], cwd='firmware')
    subprocess.check_call(['idf.py', 'build', 'flash'], cwd='firmware', env=os.environ)


def test_esp(**kwargs):
    build_flash_esp()
    exit_code = subprocess.call(['docker', 'compose', 'run', '--rm',
                                '--service-ports', '--use-aliases', 'controller', 'pdm', 'run', 'test'])
    subprocess.check_call(['docker', 'compose', 'down', '--remove-orphans'])
    exit(exit_code)



def gdb(**kwargs):
    subprocess.check_call(
        ['docker', 'compose', 'run', '--rm', 'firmware', 'gdb'])



def runserver(**kwargs):
    esp = kwargs['esp']
    subprocess.check_call(
        ['docker', 'compose', 'up','backend','unity_webgl_server','frontend','-d' ])
    if not esp:
        subprocess.check_call(
            ['docker', 'compose', 'up', 'firmware','-d'])
    subprocess.check_call(
        ['docker', 'compose', 'logs', '-f'])


def handle_sigint(signum, frame):
    down()
    print("Containers stopped. Exiting...")
    exit(0)



def main(**kwargs):
    signal.signal(signal.SIGINT, handle_sigint)

    parser = argparse.ArgumentParser(
        description='Manage the build, test, and deployment process.',
        formatter_class=argparse.RawTextHelpFormatter
        )
    subparsers = parser.add_subparsers(dest='command')

    parser_buildf = subparsers.add_parser(
        'buildf', help='Build the firmware for linux platform')
    parser_buildf.set_defaults(func=build_firmware)

    parser_build = subparsers.add_parser(
        'build', help='Build all docker images')
    parser_build.set_defaults(func=build)


    parser_build_esp = subparsers.add_parser(
        'build-esp', help='Build the firmware for esp32 platform')
    parser_build_esp.set_defaults(func=build_esp)

    parser_format = subparsers.add_parser(
        'format', help='Format all code')
    parser_format.set_defaults(func=format_code)

    parser_lint = subparsers.add_parser('lint', help='Lint all code')
    parser_lint.set_defaults(func=lint)

    parser_test = subparsers.add_parser('test', help='Run all tests')
    parser_test.set_defaults(func=test)

    parser_test_esp = subparsers.add_parser(
        'test-esp', help='Run all tests on esp32')
    parser_test_esp.set_defaults(func=test_esp)

    parser_gdb = subparsers.add_parser(
        'gdb', help='Run gdb for firmware')
    parser_gdb.set_defaults(func=gdb)

    parser_runserver = subparsers.add_parser(
        'runserver', help='Run server')
    parser_runserver.set_defaults(func=runserver)
    parser_runserver.add_argument('--esp', action='store_true', help='Run server for ESP-32 ')

    parser_down = subparsers.add_parser(
        'down', help='Stop all containers')
    parser_down.set_defaults(func=down)

    parser_build_flash_esp = subparsers.add_parser(
        'build-flash-esp', help='Build and flash firmware to esp32')
    parser_build_flash_esp.set_defaults(func=build_flash_esp)


    parsed_args, remaining_args = parser.parse_known_args()
    command_map = {
        'buildf': build_firmware,
        'build': build,
        'build-esp': build_esp,
        'format': format_code,
        'lint': lint,
        'test': test,
        'test-esp': test_esp,
        'gdb': gdb,
        'runserver': runserver,
        'down': down,
        'build-flash-esp': build_flash_esp
    }
    
    # Call the function for the first command
    command_map[parsed_args.command](**vars(parsed_args))
    
    # Loop through the remaining arguments and call corresponding functions
    while remaining_args:
        next_command = remaining_args.pop(0)
        if next_command in command_map:
            args_for_command = vars(subparsers.choices[next_command].parse_args(remaining_args))
            command_map[next_command](**args_for_command)
            break
        else:
            print(f"Unknown command: {next_command}")
            exit(1)
            
if __name__ == "__main__":
    main()

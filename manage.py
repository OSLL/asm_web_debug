#!/usr/bin/env python3

import pathlib
import argparse
import subprocess


workdir = pathlib.Path(__file__).parent


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_runserver = subparsers.add_parser("runserver", help="Run development server with debugging and live-reload enabled")
    parser_runserver.add_argument("-p", "--port", type=int, default=8080, help="Port for development server")
    parser_runserver.add_argument("-d", "--detach", action="store_true", help="Run in the background")

    parser_stopserver = subparsers.add_parser("stopserver", help="Stop development server started in detach mode")

    return parser.parse_args()


def run_docker_compose(config_path, name, env, detach=False):
    try:
        subprocess.run(
            ["docker-compose", "-f", config_path, "-p", name, "up", "--build"] + (["-d"] if detach else []),
            cwd=workdir, check=True, env=env
        )
    except KeyboardInterrupt:
        stop_docker_compose(config_path, name)
    
    if detach:
        print("To stop the server, run ./manage.py stopserver")

def stop_docker_compose(config_path, name):
    subprocess.run(["docker-compose", "-f", config_path, "-p", name, "down"])

def main():
    args = parse_args()

    if args.command == "runserver":
        run_docker_compose("docker/develop.docker-compose.yml", "asm_web_debug", {
            "APP_PORT": str(args.port)
        }, args.detach)
    
    if args.command == "stopserver":
        stop_docker_compose("docker/develop.docker-compose.yml", "asm_web_debug")


if __name__ == "__main__":
    main()

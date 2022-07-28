#!/usr/bin/env python3

import binascii
import pathlib
import argparse
import subprocess
import os


workdir = pathlib.Path(__file__).parent
args = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="asm_web_debug", help="Name for docker compose")

    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_run = subparsers.add_parser("run", help="Run server")
    parser_run.add_argument("-p", "--port", type=int, default=8080, help="Port for development server")
    parser_run.add_argument("-d", "--detach", action="store_true", help="Run in the background")
    parser_run.add_argument("--prod", action="store_true", help="Run in production mode")

    subparsers.add_parser("stop", help="Stop development server started in detach mode")
    subparsers.add_parser("shell", help="Run shell")
    parser_create_admin = subparsers.add_parser("create-admin", help="Create admin user")
    parser_create_admin.add_argument("--username", type=str)
    parser_create_admin.add_argument("--password", type=str)

    parser_restart = subparsers.add_parser("restart", help="Restart services")
    parser_restart.add_argument("service", nargs="+")

    return parser.parse_args()


def create_env_file():
    with open(workdir / ".env", "w") as f:
        print(f"AWI_SECRET_KEY={binascii.hexlify(os.urandom(32)).decode()}", file=f)


def run_docker_compose(config_path, env, detach=False):
    try:
        subprocess.run(
            ["docker-compose", "-f", config_path, "-p", args.name, "up", "--build"] + (["-d"] if detach else []),
            cwd=workdir, check=True, env={**os.environ, **env}
        )
    except KeyboardInterrupt:
        stop_docker_compose()

    if detach:
        print("To stop the server, run ./manage.py stop")
        print("To restart a service, run ./manage.py restart <web|runner|mongo|nginx>")

def stop_docker_compose():
    subprocess.run(["docker-compose", "-p", args.name, "down"])

def restart_docker_compose_services(config_path, services):
    subprocess.run(["docker-compose", "-f", config_path, "-p", args.name, "restart"] + services)

def run_command(config_path, command):
    subprocess.run(["docker-compose", "-f", config_path, "-p", args.name, "run", "web"] + command)

def main():
    global args
    args = parse_args()

    if args.command == "run":
        if not (workdir / ".env").exists():
            create_env_file()
        profile = "production" if args.prod else "develop"
        run_docker_compose(f"docker/{profile}.docker-compose.yml", {
            "APP_PORT": str(args.port)
        }, args.detach)

    if args.command == "stop":
        stop_docker_compose()

    if args.command == "restart":
        restart_docker_compose_services("docker/develop.docker-compose.yml", args.service)

    if args.command == "shell":
        run_command("docker/develop.docker-compose.yml", ["poetry", "run", "bash"])

    if args.command == "create-admin":
        cmd = ["create-admin"]
        if args.username:
            cmd += ["--username", args.username]
        if args.password:
            cmd += ["--password", args.password]
        run_command("docker/develop.docker-compose.yml", ["poetry", "run", "python", "-m", "app"] + cmd)


if __name__ == "__main__":
    main()

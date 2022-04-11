#!/usr/bin/env python3

import secrets
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
    parser_run.add_argument("-t", "--test", action="store_true", help="Run in test mode")

    subparsers.add_parser("stop", help="Stop development server started in detach mode")
    subparsers.add_parser("shell", help="Run shell")

    parser_flask = subparsers.add_parser("flask", help="Run a flask command")
    parser_flask.add_argument("args", nargs=argparse.REMAINDER)

    parser_restart = subparsers.add_parser("restart", help="Restart services")
    parser_restart.add_argument("service", nargs="+")

    return parser.parse_args()


def create_env_file():
    with open(workdir / ".env", "w") as f:
        print(f"AWI_SECRET_KEY={secrets.token_urlsafe()}", file=f)
        print(f"AWI_CONSUMER_KEYS={secrets.token_hex(8)}", file=f)
        print(f"AWI_CONSUMER_SECRETS={secrets.token_urlsafe()}", file=f)
        print(f"POSTGRES_PASSWORD={secrets.token_urlsafe()}", file=f)


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
        print("To restart a service, run ./manage.py restart <web|runner|postgres|nginx>")

def stop_docker_compose():
    subprocess.run(["docker-compose", "-p", args.name, "down"])

def build_docker_compose(config_path):
    subprocess.run(["docker-compose", "-f", config_path, "-p", args.name, "build"])

def restart_docker_compose_services(config_path, services):
    subprocess.run(["docker-compose", "-f", config_path, "-p", args.name, "restart"] + services)

def run_command(config_path, command):
    build_docker_compose(config_path)
    subprocess.run(["docker-compose", "-f", config_path, "-p", args.name, "run", "web"] + command)

def main():
    global args
    args = parse_args()

    if args.command == "run":
        if not (workdir / ".env").exists():
            create_env_file()
        profile = "production" if args.prod else "develop"
        env = { "APP_PORT": str(args.port) }
        if args.test:
            env["POSTGRES_VOLUME_BIND"] = "/dev/null:/.devnull"
            env["AWI_TEST_MODE"] = "1"
            profile = "production"
        run_docker_compose(f"docker/{profile}.docker-compose.yml", env, args.detach)

    if args.command == "stop":
        stop_docker_compose()

    if args.command == "restart":
        restart_docker_compose_services("docker/develop.docker-compose.yml", args.service)

    if args.command == "shell":
        run_command("docker/develop.docker-compose.yml", ["poetry", "run", "bash"])

    if args.command == "flask":
        run_command("docker/develop.docker-compose.yml", ["poetry", "run", "flask"] + args.args)


if __name__ == "__main__":
    main()

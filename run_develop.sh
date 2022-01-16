#!/bin/bash

docker compose -f docker/develop.docker-compose.yml -p asm_web_debug up --build

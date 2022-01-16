#!/bin/bash

set -e

cd src
RUNMODE=${1:-default} python -m app
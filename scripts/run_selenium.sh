#!/bin/bash

cd src/tests/selenium

PATH=/$PATH xvfb-run ./scripts/run_tests.sh http://127.0.0.1:5100


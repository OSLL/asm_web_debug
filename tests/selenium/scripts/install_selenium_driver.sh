#!/bin/bash

# Require https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz downloaded and extracted into tests/selenium/test_cases

if [ ! -f ./geckodriver ]; then
    echo "./geckodriver not found in selenium/test_cases, installing"
    wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
    tar -x -f geckodriver-v0.29.0-linux64.tar.gz
    rm geckodriver-v0.29.0-linux64.tar.gz
else
    echo "./geckodriver exists!"
fi

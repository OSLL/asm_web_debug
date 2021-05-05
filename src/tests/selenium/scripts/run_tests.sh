#!/bin/bash

host=${1:-"http://127.0.0.1:5100"}

./scripts/install_selenium_driver.sh

PATH=./:$PATH python3.8 main.py "${host}"

return_code=$?

if [ $return_code -eq 0 ]
then
  echo "Success tests."
else
  echo "Failure tests"
fi

cd -
exit $return_code
#!/bin/bash
set -e
export LANG=en_US.UTF-8

branch_to_deploy=${1:-"main"}

git fetch -a
git checkout ${branch_to_deploy}
git pull origin --no-edit ${branch_to_deploy}

./scripts/build_info.sh

sudo ./scripts/setup_apache_config.sh asm.moevm.info.conf

# build test images
docker-compose --project-name asmtestbuild build
# stop and remove current containers/images
docker-compose down --rmi local
# rename images if ok
docker image tag asmtestbuild_web:latest asmwebidedeploy_web:latest

docker-compose up -d

sleep 10
echo "Init logs"
docker logs `docker ps -aqf "name=asmwebidedeploy_web"`

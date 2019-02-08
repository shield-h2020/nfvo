#!/bin/bash

cleanup() {
    # Cleanup
    rm docker/docker-compose.yml
    rm docker/mongo-entrypoint/adduser.sh
}

teardown() {
    # Stop and remove containers and images
    containers=($(docker ps -aq --filter label=project\=shield-nfvo))
    docker stop "${containers[@]}"
    docker rm "${containers[@]}"
    docker rmi $(docker image list | grep docker_nfvo | head -1 | awk -F ' ' '{print $3}')
    # Cleanup
    cleanup
    return 0
}

teardown
exit 0

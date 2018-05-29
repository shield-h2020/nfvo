#!/bin/bash

cleanup() {
    # Cleanup
    rm docker/docker-compose.yml
    rm docker/mongo-entrypoint/adduser.sh
}

teardown() {
    # Stop and remove containers
    containers=($(docker ps -aq --filter label=project\=shield-nfvo))
    docker stop "${containers[@]}"
    docker rm "${containers[@]}"
    # Cleanup
    cleanup
    return 0
}

teardown
exit 0

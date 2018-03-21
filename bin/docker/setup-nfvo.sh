#!/bin/bash

REQ_PATH=${DST_PATH}/bin/deps/

# APT requirements
cat ${REQ_PATH}/nfvo-apt.txt | xargs apt-get install -y
apt-get -y install netcat

echo "Waiting for mongodb"
until nc -z ${CNTR_DB} ${DB_PORT}
do
    echo "."
    sleep 1
done

# Create database user in mongodb container
mongo --host ${CNTR_DB}:${DB_PORT} --eval "db.runCommand({ createUser: \"${DB_USERNAME}\", pwd: \"${DB_PASSWORD}\", roles: [ {role: \"readWrite\", db: \"${DB_DBNAME}\"} ]})"

# Pip requirements
pip3 install -r ${REQ_PATH}/nfvo-pip.txt
pip3 install -r ${REQ_PATH}/test-pip.txt

#
# DO NOT REMOVE THIS - LEAVE IT AS THE LAST LINE IN THE FILE.
# Convey the commands from the command line so the container does what it is intended to do once it is up and running.
exec "$@"

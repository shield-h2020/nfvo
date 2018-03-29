#!/bin/bash

REQ_PATH=${DST_PATH}/bin/deps/

# APT requirements
cat ${REQ_PATH}/nfvo-apt.txt | xargs apt-get install -y

# Pip requirements
pip3 install -r ${REQ_PATH}/nfvo-pip.txt
pip3 install -r ${REQ_PATH}/test-pip.txt

#
# DO NOT REMOVE THIS - LEAVE IT AS THE LAST LINE IN THE FILE.
# Convey the commands from the command line so the container does what it is intended to do once it is up and running.
exec "$@"
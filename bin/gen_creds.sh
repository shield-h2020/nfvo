#!/bin/bash

source utils.sh

full_path=$(dirname $(realpath $0))
cert_path=${full_path}/../cert/
mkdir -p $cert_path

# Generate server certificate and key for HTTPS connections
if [ ! -f ${cert_path}server.crt ] || [ ! -f ${cert_path}server.key ]; then
  openssl req -x509 -nodes -newkey rsa:4096 -keyout ${cert_path}server.key -out ${cert_path}server.crt -days 3650
fi

# Fill ca.crt with server crt so as to enable double-verification
test ! -s ../cert/ca.crt && cat ${cert_path}server.crt > ${cert_path}ca.crt

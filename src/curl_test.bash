#!/bin/bash

# 2-way verification
curl -k https://127.0.0.1:8000/ --cacert ../cert/server.crt -E ../cert/client.pem
#curl -k https://127.0.0.1:8000/ --key ../cert/client.key --cacert ../cert/server.crt --cert cert/client.crt

# 1-way verification
curl -k https://127.0.0.1:8000/

# No verification
curl -k http://127.0.0.1:8000/

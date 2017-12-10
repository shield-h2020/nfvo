#!/bin/bash

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


source utils.sh

full_path=$(dirname $(realpath $0))
req_path=${full_path}/deps

# APT requirements
sudo apt-get install curl
cat ${req_path}/db-apt.txt | xargs sudo apt-get install -y
cat ${req_path}/nfvo-apt.txt | xargs sudo apt-get install -y
cat ${req_path}/test-apt.txt | xargs sudo apt-get install -y

# Pip requirements
sudo pip3 install -r ${req_path}/nfvo-pip.txt
sudo pip3 install -r ${req_path}/test-pip.txt
sudo pip3 install --upgrade pip

# Generate server credentials
./gen_creds.sh
# Set-up conf files
./set_conf.sh

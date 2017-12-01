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
conf_path=${full_path}/../conf/

# Copy sample configuration files
for sample in ${conf_path}*.conf.sample; do
  final=${sample%\.*}
  if [ ! -f $final ]; then
    cp -p $sample $final
    if [[ "${final}" == *"nfvo.conf" ]] ; then
      #vm_ip=$(ip route get 8.8.8.8 | awk '/8.8.8.8/ {print $NF}')
      soub_ip=$(lxc list | grep SO-ub | awk '{print $6}')
      if [ -z $soub_ip ]; then
        soub_ip="127.0.0.1"
      fi
      # Update IP for NFVO (general)
      sed -i "s/{{general_host}}/$soub_ip/g" ${final}
      # Update IP for NFVO (packages)
      sed -i "s/{{package_host}}/$soub_ip/g" ${final}
    fi
  fi
done

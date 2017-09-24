#!/bin/bash

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
        # Update IP for NFVO (general)
        sed -i "s/{{general_host}}/${soub_ip}/" ${final}
        # Update IP for NFVO (packages)
        sed -i "s/{{package_host}}/${soub_ip}/" ${final}
      fi
    fi
done


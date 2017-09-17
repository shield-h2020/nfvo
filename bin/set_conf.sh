#!/bin/bash

full_path=$(dirname $(realpath $0))
conf_path=${full_path}/../conf/

# Copy sample configuration files
for sample in ${conf_path}*.conf.sample; do
    final=${sample%\.*}
    cp -p $sample $final
done

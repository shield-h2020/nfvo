#!/usr/bin/env bash

# Get previous information
sudo ovs-ofctl dump-flows {{ switch }}
# Delete flow
sudo ovs-ofctl del-flows {{ switch }} {{ target_filter }}

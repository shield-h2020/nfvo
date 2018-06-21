#!/usr/bin/env bash

# Get previous information
sudo ovs-ofctl dump-flows {{ flow_id }}
# Delete flow
sudo ovs-ofctl del-flows {{ flow_id }} {{ rule }}

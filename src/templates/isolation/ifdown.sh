#!/usr/bin/env bash

# Get previous information
ifconfig {{ interface_name }}
# Bringing if down
sudo ifconfig {{ interface_name }} down

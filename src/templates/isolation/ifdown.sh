#!/usr/bin/env bash

# Get previous information
sudo ifconfig {{ interface_name }}
# Bringing if down
sudo ifconfig {{ interface_name }} down

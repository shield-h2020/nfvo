#!/bin/bash

if [ -s $(realpath .) ]; then
    realpath() {
        [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
    }
fi

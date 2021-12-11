#!/bin/bash

export SRC=$(readlink --canonicalize run_client.sh)

echo "Source script: "+$SRC
echo "Check processes:"
ps -aux | grep run-client.sh
echo "Run in background"
nohup ./run-client.sh &
echo "Check processes:"
ps -aux | grep run-client.sh

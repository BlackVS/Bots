#!/bin/bash

export SRC=$(readlink --canonicalize run_client.sh)

echo "Source script: "+$SRC
echo "Check processes:"
ps -aux | grep run-client.sh
echo "Run in background"
nohup /bots/bot-clifford-run/v44/run-client.sh &
echo "Check processes:"
ps -aux | grep run-client.sh

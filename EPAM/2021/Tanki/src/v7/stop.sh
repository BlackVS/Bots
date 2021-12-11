#!/bin/bash
echo "Checking if run:"
ps -aux | grep run-client.sh

echo "Stop if tun"
pkill -f run-client.sh

echo "Checking if run:"
ps -aux | grep run-client.sh
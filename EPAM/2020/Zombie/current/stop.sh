#!/bin/bash
echo "Checking if run:"
ps -aux | grep run-client.sh

echo "Stop if tun"
pkill -f run-client.sh
pkill -f main.py

echo "Checking if run:"
ps -aux | grep run-client.sh
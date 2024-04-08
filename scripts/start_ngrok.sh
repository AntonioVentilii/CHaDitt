#!/bin/sh
# start_ngrok.sh - Script to start ngrok. Uses port 5000 by default if no port is provided.

# Set default port to 5000
default_port=5000

# Check if a port number is provided as an argument. If not, use the default port.
if [ "$#" -eq 1 ]; then
    port=$1
else
    port=$default_port
    echo "No port provided. Using default port: $port"
fi

# Start ngrok with the specified port.
ngrok http $port

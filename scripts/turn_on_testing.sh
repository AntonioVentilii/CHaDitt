#!/bin/sh
# turn_on_testing.sh - Script to turn on testing mode.

# Load the common configuration.
. ./config.sh

# Ask the user for the Local development URL.
echo "Please enter the Local Development URL:"
read -r LOCAL_DEV_URL

# Set the testing environment variables.
heroku config:set IS_TESTING=true LOCAL_DEV_URL="$LOCAL_DEV_URL" -a "$APP_NAME"

echo "Testing mode turned ON for $APP_NAME."

echo "Operation completed at $(date '+%Y-%m-%d %H:%M:%S'). Press enter to exit."
read -r

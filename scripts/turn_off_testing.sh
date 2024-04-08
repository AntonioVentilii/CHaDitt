#!/bin/sh
# turn_off_testing.sh - Script to turn off testing mode.

# Load the common configuration.
. ./config.sh

# Reset the testing environment variables.
heroku config:set IS_TESTING=false LOCAL_DEV_URL='' -a "$APP_NAME"

echo "Testing mode turned OFF for $APP_NAME."

echo "Operation completed at $(date '+%Y-%m-%d %H:%M:%S'). Press enter to exit."
read -r

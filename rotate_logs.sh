#!/bin/bash

# Define paths
LOG_FILE="/home/iman/dealosophy/cron.log"
LOG_DIR="/home/iman/dealosophy/logs"

# Make sure the logs directory exists
mkdir -p "$LOG_DIR"

# Get yesterday's date in YYYY-MM-DD format
YESTERDAY=$(date -d "yesterday" +"%Y-%m-%d")

# Check if the log file exists
if [ -f "$LOG_FILE" ]; then
    # Move and rename the file with yesterday's date
    mv "$LOG_FILE" "$LOG_DIR/$YESTERDAY.log"
    
    # Create a new empty log file
    touch "$LOG_FILE"
    
    echo "Log rotation completed: $LOG_FILE moved to $LOG_DIR/$YESTERDAY.txt"
else
    echo "Error: Log file $LOG_FILE not found"
    # Create an empty log file if it doesn't exist
    touch "$LOG_FILE"
fi
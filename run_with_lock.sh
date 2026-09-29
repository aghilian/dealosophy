#!/bin/bash

# Usage: ./run_with_lock.sh [command to run]
# Example: ./run_with_lock.sh python script.py

# Define variables
LOCK_FILE="/tmp/dealosophy_script.lock"
LOCK_TIMEOUT=3600  # 1 hour in seconds

# Check if arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No command specified"
    echo "Usage: $0 [command to run]"
    exit 1
fi

# Store the command to run
CMD="$@"

# Function to clean up lock file
cleanup() {
    rm -f "$LOCK_FILE"
    echo "Lock file removed"
    exit
}

# Set trap to ensure lock file is removed if script is interrupted
trap cleanup SIGHUP SIGINT SIGTERM

# Check if lock file exists and is not stale
if [ -e "$LOCK_FILE" ]; then
    # Get the PID from the lock file
    LOCK_PID=$(cat "$LOCK_FILE")
    
    # Check if the process is still running
    if kill -0 "$LOCK_PID" 2>/dev/null; then
        # Check if the lock is too old
        LOCK_TIME=$(stat -c %Y "$LOCK_FILE")
        CURRENT_TIME=$(date +%s)
        
        if (( CURRENT_TIME - LOCK_TIME > LOCK_TIMEOUT )); then
            echo "Warning: Stale lock found (PID: $LOCK_PID). Removing lock and continuing."
            rm -f "$LOCK_FILE"
        else
            echo "Error: Another instance is already running (PID: $LOCK_PID)"
            exit 1
        fi
    else
        echo "Warning: Found stale lock file. Removing and continuing."
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file with current PID
echo $$ > "$LOCK_FILE"
echo "Lock acquired (PID: $$)"

# Execute the command
echo "Executing: $CMD"
$CMD
EXIT_CODE=$?

# Remove lock file
rm -f "$LOCK_FILE"
echo "Lock released"

# Exit with the same exit code as the command
exit $EXIT_CODE
#!/bin/bash

SERVICE_NAME="mymusic"

set -e # Exit on error

log() {
    echo -e "\033[1;32m[INFO] $1\033[0m"
}

error() {
    echo -e "\033[1;31m[ERROR] $1\033[0m"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  error "Please run as root (sudo ./restart.sh)"
  exit 1
fi

log "Restarting $SERVICE_NAME service..."

systemctl restart $SERVICE_NAME

log "Service restarted."
log "Current Status:"
systemctl status $SERVICE_NAME --no-pager

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
  error "Please run as root (sudo ./stop.sh)"
  exit 1
fi

log "Stopping $SERVICE_NAME service..."

if systemctl is-active --quiet $SERVICE_NAME; then
    systemctl stop $SERVICE_NAME
    log "Service stopped."
else
    log "Service was already stopped."
fi

# Optional: Disable it if you don't want it to start on boot
read -p "Do you want to disable auto-start on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl disable $SERVICE_NAME
    log "Auto-start disabled."
fi

log "Done."

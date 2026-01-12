#!/bin/bash

# ====================================================
# Configuration (Please modify these before running)
# ====================================================

# 1. Git Repository URL (REQUIRED)
# Replace this with your actual repository URL
REPO_URL="https://gh-proxy.org/https://github.com/keylin/MyMusic.git"

# 2. Installation Directory
# The directory where the project will be cloned
APP_DIR="/root/MyMusic"

# 3. Systemd Service Name
SERVICE_NAME="mymusic"

# ====================================================
# Script Logic (Do not modify unless you know what you are doing)
# ====================================================

set -e # Exit on error

log() {
    echo -e "\033[1;32m[INFO] $1\033[0m"
}

error() {
    echo -e "\033[1;31m[ERROR] $1\033[0m"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  error "Please run as root (sudo ./deploy.sh)"
  exit 1
fi

# 1. System Update & Dependencies
log "Updating system and installing dependencies..."
apt update
apt install -y python3 python3-pip python3-venv git nodejs npm

# 2. Setup Application Directory
if [ -d "$APP_DIR" ]; then
    log "Directory $APP_DIR exists. Checking for updates..."
    cd "$APP_DIR"
    
    # Check if it's a git repo
    if [ ! -d ".git" ]; then
        error "$APP_DIR is not a git repository. Please handle manually."
        exit 1
    fi

    # Fetch latest info
    git fetch origin

    # Get Commit Hashes
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" == "$REMOTE" ]; then
        log "Local version matches remote ($LOCAL). No update needed."
        
        # Check if service is actually running
        if systemctl is-active --quiet $SERVICE_NAME; then
            log "Service '$SERVICE_NAME' is running. Exiting."
            exit 0
        else
            log "Service '$SERVICE_NAME' is NOT running. Proceeding to configure and start..."
            # Continue to below steps to ensure service is configured/started
        fi
    else
        log "New version found (Local: ${LOCAL:0:7}, Remote: ${REMOTE:0:7}). Updating..."
        git reset --hard origin/main
    fi
else
    log "Cloning repository to $APP_DIR..."
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

# 3. Backend Setup
log "Setting up Python backend..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# 4. Frontend Setup
log "Building Frontend..."
cd frontend
# Check if node_modules exists to save time
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# 5. Service Configuration
log "Configuring Systemd service..."

# Create service file dynamically to ensure paths are correct
cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=MyMusic Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/main.py
Environment="FLASK_DEBUG=false"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 6. Start Service
log "Starting service..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# 7. Final Output
PUBLIC_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")
log "Deployment Successful!"
log "Status: $(systemctl is-active $SERVICE_NAME)"
log "Access your application at: http://$PUBLIC_IP:8888"
log "Ensure port 8888 is open in your Security Group."

#!/bin/bash

# Configuration
VENV_NAME=".venv"
FRONTEND_DIR="frontend"
MAIN_SCRIPT="main.py"

# Function to print messages
log() {
    echo -e "\033[1;32m[INFO] $1\033[0m"
}

error() {
    echo -e "\033[1;31m[ERROR] $1\033[0m"
}

# 1. Activate Python Virtual Environment
if [ -d "$VENV_NAME" ]; then
    log "Activating virtual environment: $VENV_NAME"
    source "$VENV_NAME/bin/activate"
else
    error "Virtual environment '$VENV_NAME' not found!"
    log "Please create it first (e.g., 'python3 -m venv $VENV_NAME') or use your global python."
    read -p "Continue using global python? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 2. Check and Install Python Dependencies
if [ -f "requirements.txt" ]; then
    log "Checking/Installing Python dependencies..."
    pip install -r requirements.txt || { error "Failed to install Python dependencies"; exit 1; }
fi

# 3. Check Frontend Build
if [ -d "$FRONTEND_DIR" ]; then
    should_build=false
    
    if [ ! -d "$FRONTEND_DIR/dist" ]; then
        log "Frontend dist not found."
        should_build=true
    else
        # Check if any file in src is newer than dist
        # This is a rough check. If src is newer, ask user.
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS stat
            last_src_change=$(find "$FRONTEND_DIR/src" "$FRONTEND_DIR/public" -type f -print0 | xargs -0 stat -f %m | sort -nr | head -1)
            last_dist_change=$(stat -f %m "$FRONTEND_DIR/dist")
        else
            # Linux stat
            last_src_change=$(find "$FRONTEND_DIR/src" "$FRONTEND_DIR/public" -type f -printf '%T@\n' | sort -nr | head -1 | cut -d. -f1)
            last_dist_change=$(stat -c %Y "$FRONTEND_DIR/dist")
        fi

        if [ -n "$last_src_change" ] && [ "$last_src_change" -gt "$last_dist_change" ]; then
            log "Frontend source code appears newer than build. Rebuilding..."
            should_build=true
        fi
    fi

    if [ "$should_build" = true ]; then
        log "Building frontend..."
        cd "$FRONTEND_DIR" || exit
        
        # Install node_modules if missing
        if [ ! -d "node_modules" ]; then
            log "Installing frontend dependencies (npm install)..."
            npm install || { error "npm install failed"; exit 1; }
        fi
        
        npm run build || { error "npm build failed"; exit 1; }
        
        cd ..
    else
        log "Skipping frontend build (dist exists)."
    fi
else
    error "Frontend directory '$FRONTEND_DIR' not found!"
    exit 1
fi

# 4. Start the Application
log "Starting Application..."
if [ -f "$MAIN_SCRIPT" ]; then
    python "$MAIN_SCRIPT"
else
    error "$MAIN_SCRIPT not found!"
    exit 1
fi

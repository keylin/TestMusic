#!/bin/bash

# Configuration
SERVER_IP="121.41.170.25"
SSH_USER="root"
SSH_KEY="../music.pem" # Default path based on user input
REMOTE_APP_DIR="/root/MyMusic"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Key File
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}[Error] SSH Key file not found at: $SSH_KEY${NC}"
    echo "Please ensure the key file exists or update the SSH_KEY variable in this script."
    exit 1
fi

# Helper function for SSH commands
run_ssh() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" "$1"
}

# Helper function for SCP
run_scp() {
    local src="$1"
    local dest="$2"
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$src" "$SSH_USER@$SERVER_IP:$dest"
}

show_menu() {
    clear
    echo -e "${GREEN}=== MyMusic Remote Operations ($SERVER_IP) ===${NC}"
    echo "1. [Connect] SSH to Server"
    echo "----------------------------------------"
    echo "2. [Deploy] Trigger Remote Deploy (Git Pull + Restart)"
    echo "3. [Sync] Upload deploy.sh & manage.sh to Remote"
    echo "----------------------------------------"
    echo "4. [Service] Status"
    echo "5. [Service] Restart"
    echo "6. [Service] Stop"
    echo "7. [Service] Logs (Real-time)"
    echo "----------------------------------------"
    echo "0. Exit"
    echo -n "Enter choice [0-7]: "
}

connect_ssh() {
    echo -e "${YELLOW}Connecting to server...${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP"
}

trigger_deploy() {
    echo -e "${YELLOW}Triggering remote deployment...${NC}"
    echo "Note: This runs 'deploy.sh' on the server (git pull)."
    run_ssh "cd $REMOTE_APP_DIR && bash deploy.sh"
    read -p "Press Enter to continue..."
}

sync_scripts() {
    echo -e "${YELLOW}Uploading scripts...${NC}"
    run_scp "deploy.sh" "$REMOTE_APP_DIR/deploy.sh"
    run_scp "manage.sh" "$REMOTE_APP_DIR/manage.sh"
    run_ssh "chmod +x $REMOTE_APP_DIR/deploy.sh $REMOTE_APP_DIR/manage.sh"
    echo -e "${GREEN}Scripts updated on remote.${NC}"
    read -p "Press Enter to continue..."
}

service_cmd() {
    local cmd="$1"
    echo -e "${YELLOW}Running: ./manage.sh $cmd ...${NC}"
    if [ "$cmd" == "log" ]; then
        # For logs, we define logic to stream it or just show tail
        # manage.sh log uses 'journalctl -f', so ssh will stream it until Ctrl+C
        ssh -t -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" "cd $REMOTE_APP_DIR && bash manage.sh log"
    else
        run_ssh "cd $REMOTE_APP_DIR && bash manage.sh $cmd"
        read -p "Press Enter to continue..."
    fi
}

# Main Loop
while true; do
    show_menu
    read choice
    case $choice in
        1) connect_ssh ;;
        2) trigger_deploy ;;
        3) sync_scripts ;;
        4) service_cmd "status" ;;
        5) service_cmd "restart" ;;
        6) service_cmd "stop" ;;
        7) service_cmd "log" ;;
        0) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}"; sleep 1 ;;
    esac
done

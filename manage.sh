#!/bin/bash

SERVICE_NAME="mymusic"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper Functions
log() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root (sudo ./manage.sh)"
        exit 1
    fi
}

start_service() {
    log "Starting $SERVICE_NAME..."
    systemctl start $SERVICE_NAME
    show_status
}

stop_service() {
    log "Stopping $SERVICE_NAME..."
    systemctl stop $SERVICE_NAME
    log "Service stopped."
}

restart_service() {
    log "Restarting $SERVICE_NAME..."
    systemctl restart $SERVICE_NAME
    show_status
}

show_status() {
    echo ""
    systemctl status $SERVICE_NAME --no-pager
}

show_logs() {
    log "Showing logs (Ctrl+C to exit)..."
    journalctl -u $SERVICE_NAME -f
}

debug_system() {
    echo "========================================"
    echo "      MyMusic Debug Info"
    echo "========================================"
    
    echo -e "\n${YELLOW}[1] Service Status:${NC}"
    systemctl status $SERVICE_NAME --no-pager
    
    echo -e "\n${YELLOW}[2] Recent Logs (Last 20):${NC}"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    
    echo -e "\n${YELLOW}[3] Port 8866 Check:${NC}"
    netstat -tulpn | grep 8866 || echo "No process found on port 8866"
    
    echo -e "\n${YELLOW}[4] Curl Local Test:${NC}"
    curl -I http://127.0.0.1:8866 || echo "Curl failed."
    
    echo -e "\n${YELLOW}[5] Firewall Check:${NC}"
    if command -v ufw >/dev/null; then
        echo "UFW Status:"
        sudo ufw status | grep 8866 || echo "8866 not found in ufw rules (if ufw is active)"
    else
        echo "UFW not installed."
    fi
    
    echo "Iptables Rules (Input chain):"
    sudo iptables -L INPUT -n | grep 8866 || echo "No explicit allow rule in iptables for 8866 (might be okay if policy is ACCEPT)"
    
    echo "========================================"
}

show_menu() {
    echo -e "\n${GREEN}=== MyMusic Operations Manager ===${NC}"
    echo "1. Start Service"
    echo "2. Stop Service"
    echo "3. Restart Service"
    echo "4. Check Status"
    echo "5. View Logs (Real-time)"
    echo "6. Debug System"
    echo "0. Exit"
    echo -n "Enter choice [0-6]: "
    read choice
    
    case $choice in
        1) start_service ;;
        2) stop_service ;;
        3) restart_service ;;
        4) show_status ;;
        5) show_logs ;;
        6) debug_system ;;
        0) exit 0 ;;
        *) error "Invalid choice" ;;
    esac
}

# Main Logic
check_root

if [ -z "$1" ]; then
    # No arguments, show interactive menu
    while true; do
        show_menu
        echo -n "Press Enter to continue..."
        read
    done
else
    # Handle arguments
    case "$1" in
        start) start_service ;;
        stop) stop_service ;;
        restart) restart_service ;;
        status) show_status ;;
        log|logs) show_logs ;;
        debug) debug_system ;;
        *) 
            echo "Usage: $0 [start|stop|restart|status|log|debug]"
            exit 1
            ;;
    esac
fi

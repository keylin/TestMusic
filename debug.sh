#!/bin/bash

SERVICE_NAME="mymusic"

echo "========================================"
echo "      MyMusic Debug Script"
echo "========================================"

# 1. Check Service Status
echo ""
echo "[1] Checking Systemd Service Status..."
systemctl status $SERVICE_NAME --no-pager

# 2. Check Recent Logs
echo ""
echo "[2] Last 50 lines of Service Logs..."
journalctl -u $SERVICE_NAME -n 50 --no-pager

# 3. Check Port 8888
echo ""
echo "[3] Checking who is listening on port 8888..."
netstat -tulpn | grep 8888 || echo "No process found on port 8888"

# 4. Check Frontend Files
echo ""
echo "[4] Checking Frontend Build..."
if [ -d "/root/MyMusic/frontend/dist" ]; then
    echo "Directory /root/MyMusic/frontend/dist exists."
    ls -F /root/MyMusic/frontend/dist
else
    echo "ERROR: /root/MyMusic/frontend/dist NOT FOUND!"
fi

# 5. Local Curl Test
echo ""
echo "[5] Testing connection from localhost..."
curl -v http://127.0.0.1:8888 || echo "Curl failed."

echo ""
echo "========================================"
echo "Please copy the output above and send it back."

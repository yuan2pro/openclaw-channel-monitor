#!/bin/bash
# Install OpenClaw Monitor as a systemd service

set -e

SERVICE_NAME="openclaw-monitor"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "📦 Installing OpenClaw Monitor as systemd service..."

# Create systemd service file
sudo tee $SERVICE_FILE > /dev/null << 'EOF'
[Unit]
Description=OpenClaw Pipeline Monitor
After=network.target

[Service]
Type=simple
User=n100
WorkingDirectory=/home/n100/.openclaw/workspace/openclaw-monitor
ExecStart=/usr/bin/python3 /home/n100/.openclaw/workspace/openclaw-monitor/server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "🚀 Starting service..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo ""
echo "✅ Service installed!"
echo "📍 Dashboard: http://localhost:5050"
echo ""
echo "📋 Commands:"
echo "  sudo systemctl status $SERVICE_NAME   # Check status"
echo "  sudo systemctl restart $SERVICE_NAME  # Restart"
echo "  sudo systemctl stop $SERVICE_NAME     # Stop"
echo "  sudo journalctl -u $SERVICE_NAME -f   # View logs"
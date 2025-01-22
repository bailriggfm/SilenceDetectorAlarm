#!/bin/bash

# Define variables
USER_NAME="SilenceUser"
SERVICE_NAME="SilenceDetector"
PYTHON_SCRIPT_PATH="/opt/$SERVICE_NAME/SilenceDetector.py"
SERVICE_FILE_PATH="/etc/systemd/system/$SERVICE_NAME.service"

# Create a non-login user with Raspbian security defaults
if ! id "$USER_NAME" &>/dev/null; then
    echo "Creating non-login user: $USER_NAME"
    sudo useradd --system --no-create-home --shell /usr/sbin/nologin "$USER_NAME"
else
    echo "User $USER_NAME already exists."
fi

# Add the user to the gpio group for GPIO access
sudo usermod -aG gpio "$USER_NAME"

# Ensure the target directory exists
SCRIPT_DIR="$(dirname $PYTHON_SCRIPT_PATH)"
sudo mkdir -p "$SCRIPT_DIR"

# Copy the Python script from the same directory as this install script
INSTALL_SCRIPT_DIR="$(dirname "$0")"
if [ -f "$INSTALL_SCRIPT_DIR/SilenceDetector.py" ]; then
    echo "Copying Python script to $PYTHON_SCRIPT_PATH"
    sudo install -m 750 -o "$USER_NAME" -g "$USER_NAME" "$INSTALL_SCRIPT_DIR/SilenceDetector.py" "$PYTHON_SCRIPT_PATH"
else
    echo "Error: Python script 'SilenceDetector.py' not found in $INSTALL_SCRIPT_DIR"
    exit 1
fi

# Create the systemd service file
cat <<EOF | sudo tee "$SERVICE_FILE_PATH" > /dev/null
[Unit]
Description=Run Python Script as $USER_NAME
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
ExecStart=/usr/bin/python3 "$PYTHON_SCRIPT_PATH"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions for the service file
sudo chmod 644 "$SERVICE_FILE_PATH"

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# Confirm the service status
sudo systemctl status "$SERVICE_NAME"
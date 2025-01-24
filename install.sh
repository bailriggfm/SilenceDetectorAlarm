#!/bin/bash

#  SPDX-License-Identifier: GPL-3.0-or-later
#  Copyright (C) 2025 Bailrigg FM
#  All rights reserved.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Define variables
USER_NAME="SilenceUser"
SERVICE_NAME="SilenceDetector"
PACKAGE_NAME="BFM_Silence_Detector"
SERVICE_FILE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
VENV_DIR="/opt/$SERVICE_NAME/venv"  # Directory where the virtual environment will be created
SRC_SCRIPT_DIR="$(dirname "$0")"

echo "Installing dependencies"

# Install system dependencies
sudo apt update
sudo apt install -y python3-venv python3-pip

# Create a non-login user with Raspbian security defaults if it doesn't exist
if ! id "$USER_NAME" &>/dev/null; then
    echo "Creating non-login user: $USER_NAME"
    sudo useradd --system --shell /usr/sbin/nologin "$USER_NAME"
else
    echo "User $USER_NAME already exists."
fi

# Add the user to the gpio group for GPIO access
sudo usermod -aG gpio "$USER_NAME"

# Create the virtual environment
echo "Creating virtual environment in $VENV_DIR"
sudo mkdir -p "$VENV_DIR"
sudo python3 -m venv "$VENV_DIR"

# Install or upgrade pip in the virtual environment
echo "Installing Python dependencies in virtual environment"
sudo "$VENV_DIR/bin/pip" install --upgrade pip

# Install your Python package
if [ -f "$SRC_SCRIPT_DIR/setup.py" ]; then
    echo "Installing Python package from setup.py"
    sudo "$VENV_DIR/bin/pip" install "$SRC_SCRIPT_DIR"
elif ls "$SRC_SCRIPT_DIR"/*.whl 1> /dev/null 2>&1; then
    echo "Installing Python package from wheel file"
    sudo "$VENV_DIR/bin/pip" install "$SRC_SCRIPT_DIR"/*.whl
else
    echo "Error: No setup.py or .whl file found in $SRC_SCRIPT_DIR"
    exit 1
fi

# Copy the .env file from the same directory as this install script
if [ -f "$SRC_SCRIPT_DIR/.env" ]; then
    echo "Copying .env file to $VENV_DIR"
    sudo install -m 640 -o "$USER_NAME" -g "$USER_NAME" "$SRC_SCRIPT_DIR/.env" "$VENV_DIR/.env"
else
    echo "Error: .env file not found in $SRC_SCRIPT_DIR"
    exit 1
fi

# Create the systemd service file
cat <<EOF | sudo tee "$SERVICE_FILE_PATH" > /dev/null
[Unit]
Description=Run Python Package as $USER_NAME
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$VENV_DIR
ExecStart=$VENV_DIR/bin/python3 -m $PACKAGE_NAME
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

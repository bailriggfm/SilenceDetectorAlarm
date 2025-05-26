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

import time
import urllib.parse
import http.client
import RPi.GPIO as GPIO
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(f"Error: .env file not found in {dotenv_path}")

# Environment variables for webhook and Pushover
webhookURL = os.getenv("WEBHOOK_URL")
pushoverToken = os.getenv("PUSHOVER_TOKEN")
pushoverUser = os.getenv("PUSHOVER_USER")

if not webhookURL or not pushoverToken or not pushoverUser:
    raise ValueError("Error: Required environment variables are not set in .env file")

class PrintColours:
    ERROR = '\033[91m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

def print_error(message):
    print("[", f"{PrintColours.ERROR}ERROR", f"{PrintColours.ENDC}] ", message)

def print_ok(message):
    print("[", f"{PrintColours.OKGREEN}OK", f"{PrintColours.ENDC}] ", message)

def send_pushover(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": pushoverToken,
        "user": pushoverUser,
        "message": message,
        "priority": "1",
        "retry": "30",
        "expire": "180",
        "tags": "RelayStatusSystem"
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    print_ok("Pushover notification sent!")

def send_discord_webhook(message, title=None, color=None, footer_text=None):
    # Get the webhook URL from environment variable
    webhook_url = os.getenv('WEBHOOK_URL')

    if not webhook_url:
        raise ValueError("WEBHOOK_URL environment variable is not set")

    # Get the current timestamp in ISO 8601 format
    timestamp = datetime.now(timezone.utc).isoformat()  # UTC time in ISO 8601 format

    # Prepare the base payload
    data = {
        "content": "",  # Empty content as the embed will contain the message
        "embeds": [{
            "description": message,
            "timestamp": timestamp  # Set the timestamp to current time
        }]
    }

    # Add title if provided
    if title:
        data["embeds"][0]["title"] = title

    # Add color if provided
    if color:
        data["embeds"][0]["color"] = color

    # Add footer if provided
    if footer_text:
        data["embeds"][0]["footer"] = {
            "text": footer_text
        }

    # Send the request to the Discord webhook
    response = requests.post(webhook_url, json=data)

    # Check if the request was successful
    if response.status_code == 204:
        print("Message successfully sent!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)

# GPIO setup
GPIO_PIN = 10
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use PUD_UP since the relay is normally open

# Debounce settings
debounce_time = 0.3  # 300ms debounce
last_state = GPIO.HIGH
last_event_time = 0

try:
    print_ok("Monitoring GPIO pin for state changes...")
    while True:
        current_state = GPIO.input(GPIO_PIN)
        current_time = time.time()

        # Check for state changes with debounce
        if current_state != last_state and (current_time - last_event_time) > debounce_time:
            if current_state == GPIO.LOW:  # Relay activated
                send_pushover("Silence Detector Reset")
                send_discord_webhook(
                    "Silence Detector Reset.",
                    title="Silence Detector",
                    color=0x03f813
                )
            else:  # Relay deactivated
                send_pushover("Silence Detector Tripped")
                send_discord_webhook(
                    "Silence Detector Tripped.\nPlease check the correct studio is on air and myriad is functioning correctly",
                    title="Silence Detector",
                    color=0xf71202
                )
            last_event_time = current_time
            last_state = current_state

        time.sleep(0.05)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print_error("Monitoring interrupted by user.")
finally:
    GPIO.cleanup()
    print_ok("GPIO cleanup completed.")

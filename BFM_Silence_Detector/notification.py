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

import http.client
import urllib.parse
import requests
from datetime import datetime, timezone
from .config import load_config

# Initialize environment variables
webhook_url, pushover_token, pushover_user, _, _, pushover_token_onair, pushover_user_onair = load_config()

# for printing error messages.
class PrintColours:
    ERROR = '\033[91m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

def print_error(message):
    print("[", f"{PrintColours.ERROR}ERROR", f"{PrintColours.ENDC}] ", message)

def print_ok(message):
    print("[", f"{PrintColours.OKGREEN}OK", f"{PrintColours.ENDC}] ", message)

# Send a pushover notification.
def send_pushover(message):
    try:
        if not pushover_token or not pushover_user:
            print_error("Pushover credentials missing. Check your .env file.")
            return False

        conn = http.client.HTTPSConnection("api.pushover.net:443", timeout=10)
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": pushover_token,
            "user": pushover_user,
            "message": message,
            "priority": "1",
            "retry": "30",
            "expire": "180",
            "tags": "RelayStatusSystem"
        }), { "Content-type": "application/x-www-form-urlencoded" })
        response = conn.getresponse()
        if response.status >= 200 and response.status < 300:
            print_ok("Pushover notification sent!")
            return True
        else:
            print_error(f"Pushover API error: {response.status} {response.reason}")
            return False
    except http.client.HTTPException as e:
        print_error(f"HTTP error sending Pushover notification: {e}")
        return False
    except Exception as e:
        print_error(f"Error sending Pushover notification: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass  # Already closed or never opened

# Send a pushover notification using OnAir credentials.
def send_pushover_onair(message):
    try:
        if not pushover_token_onair or not pushover_user_onair:
            print_error("OnAir Pushover credentials missing. Check your .env file.")
            return False

        conn = http.client.HTTPSConnection("api.pushover.net:443", timeout=10)
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": pushover_token_onair,
            "user": pushover_user_onair,
            "message": message,
            "priority": "-2",
            "tags": "OnAirStatus"
        }), { "Content-type": "application/x-www-form-urlencoded" })
        response = conn.getresponse()
        if response.status >= 200 and response.status < 300:
            print_ok("OnAir Pushover notification sent!")
            return True
        else:
            print_error(f"OnAir Pushover API error: {response.status} {response.reason}")
            return False
    except http.client.HTTPException as e:
        print_error(f"HTTP error sending OnAir Pushover notification: {e}")
        return False
    except Exception as e:
        print_error(f"Error sending OnAir Pushover notification: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass  # Already closed or never opened

# Helper functions to generate status messages
def get_studio_name(pin_index):
    studio_map = {
        0: "Studio 1",
        1: "Studio 2",
        2: "Studio 3",
        3: "Studio 1",
        4: "Studio 2",
        5: "Studio 3"
    }
    return studio_map.get(pin_index, "Unknown Studio")

def get_status_type(pin_index):
    if pin_index <= 2:
        return "On Air"
    else:
        return "Mic Live"

def get_status_message(pin_index, state):
    studio = get_studio_name(pin_index)
    status_type = get_status_type(pin_index)
    status = "OFF" if state == 1 else "ON"  # GPIO.LOW (0) means ON, GPIO.HIGH (1) means OFF

    return f"{studio} {status_type}: {status}"

# Send a discord webhook message to our webhook.
def send_discord_webhook(message, title=None, color=None, footer_text=None):
    try:
        # Get the current timestamp in ISO 8601 format
        timestamp = datetime.now(timezone.utc).isoformat()

        # Prepare the base payload
        data = {
            "content": "",  # Empty content as the embed will contain the message
            "embeds": [{
                "description": message,
                "timestamp": timestamp
            }]
        }

        # Add optional parameters to embed
        if title:
            data["embeds"][0]["title"] = title
        if color:
            data["embeds"][0]["color"] = color
        if footer_text:
            data["embeds"][0]["footer"] = {"text": footer_text}

        # Send the request to the Discord webhook
        response = requests.post(webhook_url, json=data)

        # Check if the request was successful
        if response.status_code == 204:
            print("Message successfully sent!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print("An error occurred:", e)
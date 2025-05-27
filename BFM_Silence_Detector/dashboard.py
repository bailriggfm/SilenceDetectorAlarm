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
import json
import RPi.GPIO as GPIO
from .config import load_config

# Initialize environment variable
_, _, _, dashboard_host, dashboard_url, _, _ = load_config()

def send_dashboard_to_server(onAirStudio, studioAMicLive, studioCMicLive, studioBMicLive, onSilence):
    try:
        # Prepare the JSON payload
        data = {
            # as 'StudioA' or 'StudioC' or 'Automation'
            "onAirStudio": onAirStudio,
            # As boolean
            "studioAMicLive": studioAMicLive,
            "studioCMicLive": studioCMicLive,
            "studioBMicLive": studioBMicLive,
            "onSilence": onSilence
        }

        # Establish connection to the dashboard URL
        conn = http.client.HTTPSConnection(dashboard_host + ":443")
        # Send the POST request with the JSON data
        conn.request("POST", dashboard_url,
                     body=json.dumps(data),
                     headers={"Content-Type": "application/json"})
        # Get the response
        response = conn.getresponse()

        # Check if the request was successful
        if response.status == 200:
            print("Dashboard data sent successfully!")
        else:
            print(f"Failed to send notification. Status code: {response.status}")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        try:
            conn.close()
        except:
            pass  # Already closed or never opened

def send_dashboard(studioaOnAir, studiocOnAir, automationOnAir, studioAMicLive, studioCMicLive, studioBMicLive, onSilence):
    # Directly translate GPIO values to True/False with inverted logic
    studioaOnAir = (studioaOnAir == GPIO.LOW)
    studiocOnAir = (studiocOnAir == GPIO.LOW)
    automationOnAir = (automationOnAir == GPIO.LOW)
    studioAMicLive = (studioAMicLive == GPIO.LOW)
    studioCMicLive = (studioCMicLive == GPIO.LOW)
    studioBMicLive = (studioBMicLive == GPIO.LOW)
    onSilence = (onSilence == GPIO.HIGH)

    onAirStudio = ""
    if (studioaOnAir) and (not studiocOnAir) and (not automationOnAir):
        onAirStudio = "StudioA"
    if (not studioaOnAir) and (studiocOnAir) and (not automationOnAir):
        onAirStudio = "StudioC"
    if (not studioaOnAir) and (not studiocOnAir) and (automationOnAir):
        onAirStudio = "Automation"

    send_dashboard_to_server(onAirStudio, studioAMicLive, studioCMicLive, studioBMicLive, onSilence)

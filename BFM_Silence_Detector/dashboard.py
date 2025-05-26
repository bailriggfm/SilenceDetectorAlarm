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

def send_dashboard_to_server(onAirStudio, studioAMicLive, studioBMicLive, studioCMicLive, onSilence):
    # Prepare the JSON payload
    data = {
        # as 'Studio1' or 'Studio2' or 'Studio3'
        "onAirStudio": onAirStudio,
        # As boolean
        "studioAMicLive": studioAMicLive,
        "studioBMicLive": studioBMicLive,
        "studioCMicLive": studioCMicLive,
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
    # Close the connection
    conn.close()

def send_dashboard(studio1OnAir, studio2OnAir, studio3OnAir, studioAMicLive, studioBMicLive, studioCMicLive, onSilence):
    # Directly translate GPIO values to True/False with inverted logic
    studio1OnAir = (studio1OnAir == GPIO.LOW)
    studio2OnAir = (studio2OnAir == GPIO.LOW)
    studio3OnAir = (studio3OnAir == GPIO.LOW)
    studioAMicLive = (studioAMicLive == GPIO.LOW)
    studioBMicLive = (studioBMicLive == GPIO.LOW)
    studioCMicLive = (studioCMicLive == GPIO.LOW)
    onSilence = (onSilence == GPIO.HIGH)

    onAirStudio = ""
    if (studio1OnAir) and (not studio2OnAir) and (not studio3OnAir):
        onAirStudio = "Studio1"
    if (not studio1OnAir) and (studio2OnAir) and (not studio3OnAir):
        onAirStudio = "Studio2"
    if (not studio1OnAir) and (not studio2OnAir) and (studio3OnAir):
        onAirStudio = "Studio3"

    send_dashboard_to_server(onAirStudio, studioAMicLive, studioBMicLive, studioCMicLive, onSilence)

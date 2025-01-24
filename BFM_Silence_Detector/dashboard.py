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
from config import load_config

# Initialize environment variable
_, _, _, dashboard_url = load_config()

def send_dashboard(onAirStudio, studioAMicLive, studioBMicLive, studioCMicLive, onSilence):
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
    conn = http.client.HTTPSConnection(dashboard_url + ":443")
    # Send the POST request with the JSON data
    conn.request("POST", "/1/messages.json",
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

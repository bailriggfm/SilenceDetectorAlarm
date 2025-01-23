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

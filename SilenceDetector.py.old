import time
import urllib.parse
import http.client
import RPi.GPIO as GPIO
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import requests
import json

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
dashboardURL = os.getenv("DASHBOARD_URL")

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

def send_dashboard(onAirStudio, studioAMicLive, studioBMicLive, studioCMicLive, onSilence):
    # Prepare the JSON payload
    data = {
        "onAirStudio": onAirStudio,
        "studioAMicLive": studioAMicLive,
        "studioBMicLive": studioBMicLive,
        "studioCMicLive": studioCMicLive,
        "onSilence": onSilence
    }

    # Establish connection to the dashboard URL
    conn = http.client.HTTPSConnection(dashboardURL + ":443")
    # Send the POST request with the JSON data
    conn.request("POST", "/1/messages.json",
                 body=json.dumps(data),
                 headers={"Content-Type": "application/json"})
    # Get the response
    response = conn.getresponse()

    # Check if the request was successful
    if response.status == 200:
        print("Pushover notification sent successfully!")
    else:
        print(f"Failed to send notification. Status code: {response.status}")
    # Close the connection
    conn.close()

# GPIO setup
GPIO_PIN = 10
NEW_GPIO_PINS = [17, 27, 22, 5, 6, 13]  # Add your new GPIO pins here
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use PUD_UP since the relay is normally open
for pin in NEW_GPIO_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup for new GPIO pins

# Debounce settings
debounce_time = 0.3  # 300ms debounce
last_state = GPIO.HIGH
last_event_time = 0

# Initialize states for new GPIO pins
last_states_new_gpio = {pin: GPIO.input(pin) for pin in NEW_GPIO_PINS}

try:
    print_ok("Monitoring GPIO pins for state changes...")
    while True:
        # Monitor the original GPIO pin (GPIO_PIN)
        current_state = GPIO.input(GPIO_PIN)
        current_time = time.time()

        # Check for state changes with debounce on the original GPIO pin
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
                    "Silence Detector Tripped.",
                    title="Silence Detector",
                    footer="Please check the correct studio is on air and myriad is functioning correctly",
                    color=0xf71202
                )
            # Call send_dashboard for the original GPIO pin state change (to be fixed later)
            send_dashboard("onAirStudio", "studioAMicLive", "studioBMicLive", "studioCMicLive", "onSilence")

            last_event_time = current_time
            last_state = current_state

        # Monitor the new GPIO pins
        for pin in NEW_GPIO_PINS:
            current_pin_state = GPIO.input(pin)
            if current_pin_state != last_states_new_gpio[pin]:
                # Call send_dashboard for new GPIO pin state change (to be fixed later)
                send_dashboard("onAirStudio", "studioAMicLive", "studioBMicLive", "studioCMicLive", "onSilence")
                last_states_new_gpio[pin] = current_pin_state

        time.sleep(0.05)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print_error("Monitoring interrupted by user.")
finally:
    GPIO.cleanup()
    print_ok("GPIO cleanup completed.")

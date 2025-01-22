import time
import urllib.parse
import http.client
import RPi.GPIO as GPIO
#from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from dotenv import load_dotenv
import os

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

#def send_discord_webhook(title, message, colour):
#    webhook = DiscordWebhook(url=webhookURL, rate_limit_retry=True)
#    embed = DiscordEmbed(title=title, description=message, color=colour)
#    embed.set_footer(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Timestamp
#    webhook.add_embed(embed)
#    response = webhook.execute()
#    if response.status_code == 200:
#        print_ok("Discord notification sent!")
#    else:
#        print_error(f"Failed to send Discord notification. Status: {response.status_code}")

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
                send_pushover("Relay Activated: Circuit Closed")
                # Uncomment and update the following if using Discord webhook
                # send_discord_webhook(
                #     "Relay Activated",
                #     "The relay circuit is now closed.",
                #     "#f71202"
                # )
            else:  # Relay deactivated
                send_pushover("Relay Deactivated: Circuit Open")
                # Uncomment and update the following if using Discord webhook
                # send_discord_webhook(
                #     "Relay Deactivated",
                #     "The relay circuit is now open.",
                #     "#03f813"
                # )
            last_event_time = current_time
            last_state = current_state

        time.sleep(0.05)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print_error("Monitoring interrupted by user.")
finally:
    GPIO.cleanup()
    print_ok("GPIO cleanup completed.")

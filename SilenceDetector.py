'''
SilenceDetector V3!

Now with new features such as:
    Discord web hooks!

Possible V4 Ideas:
    We add silly messages to the discord embeds
    We pull data such as current show and on air studio, current media item and add it to the report
     
'''
import urllib, http.client
import RPI.GPIO as GPIO
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import os

webhookURL = os.getenv("WEBHOOK_URL")
pushoverToken = os.getenv("PUSHOVER_TOKEN")
pushoverUser = os.getenv("PUSHOVER_USER")


class printColours:
    ERROR = '\033[91m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'

def printError(message):
    print("[",f"{printColours.ERROR}ERROR",f"{printColours.ENDC}] ", message)

def printOK(message):
    print("[",f"{printColours.OKGREEN}OK",f"{printColours.ENDC}] ", message)

def sendPushover(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "pushoverToken",
        "user": "pushoverUser",
        "message": message,
        "sound": "gamelan",
        "priority": "1",
        "retry": "30",
        "expire": "180",
        "tags": "EngineeringAlertSystem"
    }), { "Content-type": "application/x-www-form-urlencoded" })
    res = conn.getresponse()
    printOK("Pushover notification sent!")    

def sendDiscordWebHook(title, message, colour):    
    webhook = DiscordWebhook(url="webhookURL", rate_limit_retry=True, content="Webhook Message")
    embed = DiscordEmbed(title=title, description=message, color=colour)    
    embed.set_footer(text=datetime.now().strftime("%D/%M/%Y %H:%M:%S")) #Timestamp Here!
    webhook.add_embed(embed)
    response = webhook.execute()
    return(response)




GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


while(True):
    #Wait for alarm to activate
    GPIO.wait_for_edge(10, GPIO.RISING)
    sendPushover("Silence Detector Tripped")
    sendDiscordWebHook("Silence Detector Tripped", "Someone should probably go fix that", "##f71202")
    #Wait for alarm to reset
    GPIO.wait_for_edge(10, GPIO.FALLING)
    sendPushover("Silence Detector Reset")
    sendDiscordWebHook("Silence Detector Reset", "_and now back to our reguarly scheduled programming_", "#03f813")



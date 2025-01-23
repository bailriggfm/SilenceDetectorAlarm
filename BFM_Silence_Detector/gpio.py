import time
import RPi.GPIO as GPIO
from notification import send_pushover, send_discord_webhook, send_dashboard

# Named constants for our GPIO pins
SilenceDetector_PIN = 10
Studio_1_OnAir_PIN = 17
Studio_2_OnAir_PIN = 27
Studio_3_OnAir_PIN = 22
Studio_1_MicLive_PIN = 5
Studio_2_MicLive_PIN = 6
Studio_3_MicLive_PIN = 13

# Define a list of the new GPIO pin constants
OnAir_MicLive_GPIO_Pins = [
    Studio_1_OnAir_PIN,
    Studio_2_OnAir_PIN,
    Studio_3_OnAir_PIN,
    Studio_1_MicLive_PIN,
    Studio_2_MicLive_PIN,
    Studio_3_MicLive_PIN
]

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SilenceDetector_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Use PUD_UP since the relay is normally open
    for pin in OnAir_MicLive_GPIO_Pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup for new GPIO pins

def monitor_gpio():
    # Debounce settings
    debounce_time = 0.3  # 300ms debounce
    silence_last_state = GPIO.HIGH
    last_event_time = 0

    # Initialize states for new GPIO pins
    last_states_OnAir_MicLive = {pin: GPIO.input(pin) for pin in OnAir_MicLive_GPIO_Pins}
    last_event_times_OnAir_MicLive = {pin: 0 for pin in OnAir_MicLive_GPIO_Pins}  # Track debounce times

    try:
        print("Monitoring GPIO pins for state changes...")
        while True:
            # Monitor the original GPIO pin (SilenceDetector_PIN)
            current_state = GPIO.input(SilenceDetector_PIN)
            current_time = time.time()

            # Check for state changes with debounce on the original GPIO pin
            if current_state != silence_last_state and (current_time - last_event_time) > debounce_time:
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
                send_dashboard("onAirStudio", "studioAMicLive", "studioBMicLive", "studioCMicLive", "onSilence")

                last_event_time = current_time
                silence_last_state = current_state

            # Monitor the OnAir and MicLive GPIO pins with debounce
            for pin in OnAir_MicLive_GPIO_Pins:
                current_pin_state = GPIO.input(pin)
                current_time = time.time()
                if current_pin_state != last_states_OnAir_MicLive[pin] and (current_time - last_event_times_OnAir_MicLive[pin]) > debounce_time:
                    send_dashboard("onAirStudio", "studioAMicLive", "studioBMicLive", "studioCMicLive", "onSilence")
                    last_states_OnAir_MicLive[pin] = current_pin_state
                    last_event_times_OnAir_MicLive[pin] = current_time

            time.sleep(0.05)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("Monitoring interrupted by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")

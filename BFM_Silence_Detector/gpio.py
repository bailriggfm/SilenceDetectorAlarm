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
                        "Silence Detector Tripped.\nPlease check the correct studio is on air and myriad is functioning correctly",
                        title="Silence Detector",
                        color=0xf71202
                    )

                last_event_time = current_time
                silence_last_state = current_state

                # Update the dashboard
                send_dashboard(
                    last_states_OnAir_MicLive[0],
                    last_states_OnAir_MicLive[1],
                    last_states_OnAir_MicLive[2],
                    last_states_OnAir_MicLive[3],
                    last_states_OnAir_MicLive[4],
                    last_states_OnAir_MicLive[5],
                    silence_last_state
                )


            # Monitor the OnAir and MicLive GPIO pins with debounce
            for pin in OnAir_MicLive_GPIO_Pins:
                current_pin_state = GPIO.input(pin)
                current_time = time.time()
                if current_pin_state != last_states_OnAir_MicLive[pin] and (current_time - last_event_times_OnAir_MicLive[pin]) > debounce_time:
                    last_states_OnAir_MicLive[pin] = current_pin_state
                    last_event_times_OnAir_MicLive[pin] = current_time

                    # Update the dashboard
                    send_dashboard(
                        last_states_OnAir_MicLive[0],
                        last_states_OnAir_MicLive[1],
                        last_states_OnAir_MicLive[2],
                        last_states_OnAir_MicLive[3],
                        last_states_OnAir_MicLive[4],
                        last_states_OnAir_MicLive[5],
                        silence_last_state
                    )

            time.sleep(0.05)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("Monitoring interrupted by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")

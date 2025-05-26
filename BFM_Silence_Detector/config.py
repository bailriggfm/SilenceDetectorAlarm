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

import os
from dotenv import load_dotenv

# Load environment variables from .env file
def load_config():
    # Check multiple possible locations for .env file
    potential_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),  # Package directory
        os.path.join(os.getcwd(), ".env"),  # Working directory
        os.path.join(os.path.expanduser("~"), ".env"),  # Home directory
        "/opt/SilenceDetector/venv/.env"  # Installation directory
    ]

    for dotenv_path in potential_paths:
        if os.path.exists(dotenv_path):
            print(f"Loading configuration from {dotenv_path}")
            load_dotenv(dotenv_path)
            break
    else:
        print("Warning: No .env file found in any of the expected locations")

    # Environment variables for webhook and Pushover
    webhook_url = os.getenv("WEBHOOK_URL")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")
    dashboard_host = os.getenv("DASHBOARD_HOST")
    dashboard_url = os.getenv("DASHBOARD_URL")
    pushover_token_onair = os.getenv("PUSHOVER_TOKEN_ONAIR")
    pushover_user_onair = os.getenv("PUSHOVER_USER_ONAIR")

    if not webhook_url or not pushover_token or not pushover_user or not dashboard_url:
        raise ValueError("Error: Required environment variables are not set in .env file")

    return webhook_url, pushover_token, pushover_user, dashboard_host, dashboard_url, pushover_token_onair, pushover_user_onair

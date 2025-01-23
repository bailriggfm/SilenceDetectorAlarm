import os
from dotenv import load_dotenv

# Load environment variables from .env file
def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(script_dir, ".env")

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        raise FileNotFoundError(f"Error: .env file not found in {dotenv_path}")

    # Environment variables for webhook and Pushover
    webhook_url = os.getenv("WEBHOOK_URL")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")
    dashboard_url = os.getenv("DASHBOARD_URL")

    if not webhook_url or not pushover_token or not pushover_user or not dashboard_url:
        raise ValueError("Error: Required environment variables are not set in .env file")

    return webhook_url, pushover_token, pushover_user, dashboard_url

import os
import requests
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT").lower()
SLACK_WEBHOOK_URL = os.getenv(
    "SLACK_WEBHOOK_URL_DEV" if ENVIRONMENT == "dev" else "SLACK_WEBHOOK_URL_PROD"
)

def send_slack_message(message: str):
    """Send a message to Slack using the configured webhook."""
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL is not set.")
        return

    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            logger.error(f"Slack webhook failed: {response.status_code} {response.text}")
    except Exception as e:
        logger.exception(f"Exception sending to Slack: {e}")

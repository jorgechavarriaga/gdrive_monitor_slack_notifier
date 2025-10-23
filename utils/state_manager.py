import os
import json
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Define the path to the state file
path = os.getenv("STATE_FILE")
STATE_FILE = Path(path)


def load_state() -> Dict:
    """
    Load the previously saved state (e.g., pageToken) from the state file.

    Returns:
        Dict: A dictionary representing the stored state. Empty if no file exists.
    """
    if STATE_FILE.exists():
        try:
            content = STATE_FILE.read_text()
            state = json.loads(content)
            logger.debug(f"State loaded: {state}")
            return state
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return {}
    else:
        logger.info("State file not found. Returning empty state.")
        return {}


def save_state(state: Dict):
    """
    Save the current state (e.g., updated pageToken) to the state file.

    Args:
        state (Dict): The state dictionary to persist.
    """
    try:
        STATE_FILE.write_text(json.dumps(state))
        logger.debug(f"State saved: {state}")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

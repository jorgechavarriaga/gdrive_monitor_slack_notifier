import os
from pathlib import Path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)
load_dotenv()

SCOPES = os.getenv("SCOPES")


def get_drive_service() -> any:
    """
    Authenticate and return a Google Drive service instance.

    This function handles OAuth2 authentication using saved credentials.
    If the token is expired or missing, it refreshes or initiates a new flow.
    Returns:
        service (googleapiclient.discovery.Resource): Authenticated Drive API client
    """
    creds = None
    token_file = Path("token.json")
    credentials_file = Path("credentials.json")

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials.")
            creds.refresh(Request())
        else:
            logger.info("Starting OAuth2 flow to obtain new credentials.")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())
        logger.info("New credentials saved to token.json")

    logger.info("Google Drive service initialized successfully.")
    return build("drive", "v3", credentials=creds)

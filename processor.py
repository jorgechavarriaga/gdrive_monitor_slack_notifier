import os
import pytz
import time
from datetime import datetime
from utils.slack_notifier import send_slack_message
from utils.drive_service import get_drive_service
from utils.state_manager import load_state, save_state
from utils.drive_utils import get_start_token, build_path_index, is_descendant, resolve_path
from utils.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

# Config
ROOT_NAME = os.getenv("ROOT_NAME")
FOLDER_ID = os.getenv("FOLDER_ID")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
LOCAL_ZONE = os.getenv("LOCAL_ZONE", "America/Toronto")

# Logger
log = get_logger(__name__)


def run_monitor():
    """
    Run the main monitoring loop to track Google Drive changes under a specific folder.
    Sends Slack notifications on file modifications or deletions.
    """
    service = get_drive_service()
    state = load_state()
    page_token = state.get("pageToken")

    if not page_token:
        page_token = get_start_token(service)
        state["pageToken"] = page_token
        save_state(state)

    parent_tree_cache = {}
    log.info(f"Monitoring folder: {ROOT_NAME} ({FOLDER_ID}) every {POLL_SECONDS}s")

    path_index = build_path_index(service, FOLDER_ID)

    while True:
        try:
            req = service.changes().list(
                pageToken=page_token,
                includeRemoved=True,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageSize=100,
                fields=(
                    "nextPageToken,newStartPageToken,changes("
                    "time,removed,fileId,"
                    "file(id,name,trashed,mimeType,parents,"
                    "owners(emailAddress),lastModifyingUser(emailAddress),modifiedTime))"
                )
            )

            while req is not None:
                res = req.execute()
                for ch in res.get("changes", []):
                    file = ch.get("file")
                    removed = ch.get("removed", False)
                    if removed or not file:
                        continue

                    is_folder = file.get("mimeType") == "application/vnd.google-apps.folder"
                    event = "TRASHED" if file.get("trashed") else "MODIFIED"
                    change_type = "FOLDER" if is_folder else "FILE"


                    if is_descendant(service, file, FOLDER_ID, parent_tree_cache):
                        event = "TRASHED" if file.get("trashed") else "MODIFIED"
                        file_id = file["id"]
                        owner = ", ".join(o.get("emailAddress", "") for o in file.get("owners", []))
                        last_mod_user = file.get("lastModifyingUser", {}).get("emailAddress", "UNKNOWN")
                        when_raw = ch.get("time", "")

                        # Convert UTC timestamp to local timezone
                        local_tz = pytz.timezone(LOCAL_ZONE)
                        utc_time = datetime.fromisoformat(when_raw.replace("Z", "+00:00"))
                        when = utc_time.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")

                        # Resolve full path
                        path = path_index.get(file_id) or resolve_path(service, file_id, path_index)
                        path_index[file_id] = path

                        # Slack message format
                        slack_msg = (
                            f"[{event}] \n🕓 *Time:* {when} ({LOCAL_ZONE})\n📁 *Path:* {path}\n"
                            f"📦 *Type:* {change_type}\n👤 *Owner:* {owner}\n✏️ *Modified by:* {last_mod_user}\n"
                        )

                        send_slack_message(slack_msg)
                        log.info(f"[{event}]\n{when} ({LOCAL_ZONE})\nTYPE: {change_type}\nPATH: {path}\nOWNER: {owner}\nMODIFIED BY: {last_mod_user}\n\n")


                # Update tokens for next poll
                page_token = res.get("nextPageToken", page_token)
                if not res.get("nextPageToken") and res.get("newStartPageToken"):
                    page_token = res["newStartPageToken"]
                    state["pageToken"] = page_token
                    save_state(state)
                    break

                req = service.changes().list_next(previous_request=req, previous_response=res)

        except Exception as e:
            log.error(f"Exception during monitoring: {e}")

        time.sleep(POLL_SECONDS)





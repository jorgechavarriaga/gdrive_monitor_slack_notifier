import os
import time
from typing import Dict, Optional
from googleapiclient.discovery import Resource
from utils.logger import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)
ROOT_NAME = os.getenv("ROOT_NAME")

def get_start_token(service: Resource) -> str:
    """
    Retrieves the current start page token from the Google Drive API.
    This token is used to begin monitoring changes.
    """
    logger.info("[*] Fetching start page token...")
    while True:
        try:
            token = service.changes().getStartPageToken().execute()["startPageToken"]
            logger.info(f"[+] Start page token retrieved: {token}")
            return token
        except Exception as e:
            logger.error(f"[-] Error retrieving start token: {e}")
            time.sleep(3)


def build_path_index(service: Resource, root_folder_id: str) -> Dict[str, str]:
    """
    Recursively builds a mapping of file IDs to their full folder paths starting from the root folder.
    This helps resolve a file path quickly without making repeated API calls.
    """
    logger.info("[*] Building folder path index recursively...")
    path_index = {}

    def walk(folder_id: str, path: str):
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        page_token = None

        while True:
            try:
                res = (
                    service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name)",
                        pageToken=page_token,
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                    )
                    .execute()
                )

                for folder in res.get("files", []):
                    fid = folder["id"]
                    pname = folder["name"]
                    new_path = f"{path}/{pname}"
                    path_index[fid] = new_path
                    walk(fid, new_path)

                page_token = res.get("nextPageToken", None)
                if not page_token:
                    break
            except Exception as e:
                logger.error(f"[-] Error walking folder: {e}")
                time.sleep(3)

    path_index[root_folder_id] = ROOT_NAME
    walk(root_folder_id, ROOT_NAME)
    logger.info(f"[+] Completed building path index ({len(path_index)} entries)")
    return path_index


def is_descendant(service: Resource, file: dict, root_id: str, cache: Dict[str, Optional[bool]]) -> bool:
    """
    Checks if the given file is a descendant of the root folder.
    Uses a cache to avoid redundant checks.
    """
    parents = file.get("parents", [])
    if not parents:
        return False

    for pid in parents:
        if pid in cache:
            return cache[pid]
        try:
            f = service.files().get(fileId=pid, fields="id, name, parents", supportsAllDrives=True).execute()
            if f["id"] == root_id:
                cache[pid] = True
                return True
            else:
                cache[pid] = is_descendant(service, f, root_id, cache)
                return cache[pid]
        except Exception as e:
            logger.error(f"[-] Error checking descendant: {e}")
            time.sleep(2)
            return False


def resolve_path(service: Resource, file_id: str, path_index: Dict[str, str]) -> str:
    """
    Reconstructs the full path of a file by traversing its parent folders.
    Uses the path_index for any folders already indexed.
    """
    parts = []
    current_id = file_id

    while True:
        try:
            if current_id in path_index:
                parts.append(path_index[current_id])
                break

            file = service.files().get(
                fileId=current_id,
                fields="id, name, parents",
                supportsAllDrives=True
            ).execute()

            parts.append(file["name"])
            parents = file.get("parents", [])
            if not parents:
                break
            current_id = parents[0]
        except Exception as e:
            logger.warning(f"[!] Error resolving path: {e}")
            break

    return "/".join(reversed(parts))

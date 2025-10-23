# 📦 Google Drive Change Monitor & Slack Notifier
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-yellow?logo=docker)](https://www.docker.com/)
[![Slack](https://img.shields.io/badge/Slack-Webhooks-green?logo=slack)](https://api.slack.com/messaging/webhooks)
[![Google Drive API](https://img.shields.io/badge/Google%20Drive-API-red?logo=google-drive)](https://developers.google.com/drive)

A minimal and production‑ready Python application to monitor any folder in Google Drive (via Drive API) and send Slack notifications for detected changes, including:

- ✅ File creation / modification
- 🗑️ File deletion (trashed)
- 📁 Folder creation / rename
- ❌ Folder deletion (trashed)

This app is fully generic and environment-agnostic, requiring only a folder ID and a Slack webhook URL.

---

## 🚀 Tech Stack

- **Python 3.11**
- **Google Drive API (readonly)**
- **Slack Webhooks**
- **Docker & docker-compose**
- **Dotenv (.env config)**
- **OAuth2 credentials flow**

---

## 🔧 Features

- 🔁 Real‑time change detection via changes().list()
- 🧠 Maintains state between runs to avoid missing changes
- 🌍 Converts timestamps to your local timezone
- 🔔 Sends notifications to Slack with rich formatting
- 🐳 Dockerized for easy deployment on servers, VMs, or NAS devices
- 🔐 OAuth2 token persistence
- 🧪 Supports dev and prod environments via .env config
- 🧼 Clean, modular codebase – easy to extend

---

## 📁 Folder Structure

```
.
├── app/
│ ├── init.py
│ ├── main.py # Entry point
│ ├── processor.py # Core loop
│ └── utils/
│   ├── drive_service.py # Auth & API access
│   ├── drive_utils.py # Helpers for change detection
│   ├── slack_notifier.py # Slack message sender
│   ├── state_manager.py # Handles saved state
│   └── logger.py # Centralized logger
├── .env # Environment variables (not committed)
├── .env.example # Example template
├── drive_watch_state.json # Persistent state
├── requirements.txt
├── docker-compose.yml
├── .gitignore
├── .dockerignore
└── README.md
```

---

## 🚀 How It Works

1. Connects to the Google Drive API using `credentials.json` + `token.json`.
2. Checks for changes in a specific folder (by ID).
3. Sends a message to Slack if a file is **modified** or **trashed**.
4. Stores a `pageToken` in a local JSON file to avoid reprocessing events.

---

## 🛠️ Setup (Locally)

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-org/drive-watcher.git
   cd drive-watcher
   ```
2. **Create .env**

```
ENVIRONMENT=dev
SLACK_WEBHOOK_URL_DEV=https://hooks.slack.com/services/xxx
SLACK_WEBHOOK_URL_PROD=https://hooks.slack.com/services/yyy
FOLDER_ID=your-folder-id
ROOT_NAME=your-folder-root-name
POLL_SECONDS=60
LOCAL_ZONE=America/Toronto
STATE_FILE=drive_watch_state.json
```

3. **Install dependencies**

```
pip install -r requirements.txt
```

4. **Run**

```
python app/main.py
```

---

### 🐳 Run with Docker

Automatically mounts token/state files and runs in background.

```
docker-compose up --build -d
```

To stop:

```
docker-compose down
```

---

### 📦 requirements.txt

```
# Env var management
python-dotenv==1.0.0

# Google Drive API
google-auth==2.23.0
google-auth-oauthlib==1.0.0
google-api-python-client==2.107.0

# Slack integration
requests==2.31.0

# Timezone handling
pytz==2023.3.post1
```

---

### 📄 .gitignore

```
# Python
__pycache__/
*.pyc

# Virtualenv
.venv/
env/

# Editor configs
.vscode/
.idea/

# Secrets
.env
credentials.json
token.json
drive_watch_state.json

# OS
.DS_Store

# Docker
*.log
```

---

### 📄 .dockerignore

```
__pycache__/
*.pyc
.env
token.json
credentials.json
*.log
.vscode/
.idea/
.DS_Store
```

---

### ✅ Environment Support

Your .env file determines the Slack webhook used:

ENVIRONMENT=dev → uses SLACK_WEBHOOK_URL_DEV

ENVIRONMENT=prod → uses SLACK_WEBHOOK_URL_PROD


---

### 📌 Notes
Google Drive API must be enabled in your GCP project.

credentials.json must be downloaded from Google Cloud Console (OAuth 2.0).

First run will trigger browser auth to create token.json.

---

### 📬 Slack Message Example
- [MODIFIED]
- 🕓 **Time:** 2025-10-23 15:24:00 (America/Toronto)
- 📁 **Path:** ROOT/HR/Policies/Leave.pdf
- 📦 **Type**: FILE
- 👤 **Owner:** hr@company.com
- ✏️ **Modified by:** jorge.chavarriaga@chavazystem.tech

---

### 👨‍💻 Author

👤 **Jorge Chavarriaga**  
*Full Stack Developer – ChavaZystem Tech*  
🌐 [www.chavazystem.tech](https://chavazystem.tech)  
🔗 [LinkedIn](https://www.linkedin.com/in/jorge-chavarriaga)

import requests
import sys
from datetime import datetime, timedelta, timezone

# Configuration
RADARR_API_KEY = "your_radarr_api_key"
SONARR_API_KEY = "your_sonarr_api_key"
RADARR_URL = "http://localhost:7878/api/v3"
SONARR_URL = "http://localhost:8989/api/v3"
ERROR_STATUSES = {"warning", "unknown", "failed"}
WARNING_THRESHOLD_HOURS = 48

# Define log file
log_file = "log.txt"

# Function to append failed items to log
def log_failure(item, type, reason="Failure"):
    with open(log_file, "a") as log:
        log.write(f"{type} {reason} was in state {item.get('status', 'unknown')}: {item['title']} (ID: {item.get('movieId') or item.get('seriesId')})\n")

# Function to get queue status
def get_queue(url, api_key):
    response = requests.get(f"{url}/queue/details", headers={"X-Api-Key": api_key})
    return response.json()

# Function to handle failed complete items
def handle_failure(item, type, url, api_key, reason="Failure"):
    print(f"Handling {reason.lower()} for {item['title']} (ID: {item.get('movieId') or item.get('seriesId')})")
    log_failure(item, type, reason)

    response = requests.delete(
        f"{url}/queue/{item['id']}?removeFromClient=false&blocklist=true&skipRedownload=false&changeCategory=false",
        headers={"X-Api-Key": api_key}
    )
    print(f"Queue removal response: {response.status_code}, {response.text}")
    
# Function to handle stuck or partial items
def handle_failure_stuck(item, type, url, api_key, reason="Failure"):
    print(f"Handling {reason.lower()} for {item['title']} (ID: {item.get('movieId') or item.get('seriesId')})")
    log_failure(item, type, reason)

    response = requests.delete(
        f"{url}/queue/{item['id']}?removeFromClient=true&blocklist=true&skipRedownload=false&changeCategory=false",
        headers={"X-Api-Key": api_key}
    )
    print(f"Queue removal response: {response.status_code}, {response.text}")
    
# Function to check if item is completed and has a warning status
def is_stale_completed(item):
    return item.get('status') == "completed" and item.get('trackedDownloadStatus') == "warning"

# Function to check if item is stuck in warning or queued
def is_stuck_warning(item):
    if item.get('status') not in ("warning", "queued"):
        return False
    warning_time_str = item.get('added')
    if not warning_time_str:
        return False
    try:
        warning_time = datetime.strptime(warning_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - warning_time > timedelta(hours=WARNING_THRESHOLD_HOURS)
    except Exception as e:
        print(f"Time parse error (warning): {e}")
        return False

# Process Radarr queue
radarr_failed = False
for item in get_queue(RADARR_URL, RADARR_API_KEY):
    if item.get('status') == "completed":
        if item.get('status') in ERROR_STATUSES:
            radarr_failed = True
            handle_failure(item, "Radarr", RADARR_URL, RADARR_API_KEY)
        elif is_stale_completed(item):
            radarr_failed = True
            handle_failure(item, "Radarr", RADARR_URL, RADARR_API_KEY, reason="Stale")
    elif is_stuck_warning(item):
        radarr_failed = True
        handle_failure_stuck(item, "Radarr", RADARR_URL, RADARR_API_KEY, reason="Stuck")

# Process Sonarr queue
sonarr_failed = False
for item in get_queue(SONARR_URL, SONARR_API_KEY):
    if item.get('status') == "completed":
        if item.get('status') in ERROR_STATUSES:
            sonarr_failed = True
            handle_failure(item, "Sonarr", SONARR_URL, SONARR_API_KEY)
        elif is_stale_completed(item):
            sonarr_failed = True
            handle_failure(item, "Sonarr", SONARR_URL, SONARR_API_KEY, reason="Stale")
    elif is_stuck_warning(item):
        sonarr_failed = True
        handle_failure_stuck(item, "Sonarr", SONARR_URL, SONARR_API_KEY, reason="Stuck")

# Final status
if not radarr_failed and not sonarr_failed:
    print("Everything looks good! Nothing to see here.")
else:
    print("Failed items logged to file.")
    

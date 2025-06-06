import requests

# Configuration
RADARR_API_KEY = "your_radarr_api_key"
SONARR_API_KEY = "your_sonarr_api_key"
RADARR_URL = "http://localhost:7878/api/v3"
SONARR_URL = "http://localhost:8989/api/v3"
ERROR_STATUSES = {"error", "warning", "unknownError", "unknownWarning"}

# Function to get queue status from Radarr
def get_radarr_queue():
    response = requests.get(f"{RADARR_URL}/queue", headers={"X-Api-Key": RADARR_API_KEY})
    return response.json().get('records', [])

# Function to get queue status from Sonarr
def get_sonarr_queue():
    response = requests.get(f"{SONARR_URL}/queue", headers={"X-Api-Key": SONARR_API_KEY})
    return response.json().get('records', [])

# Function to handle failed items in Radarr
def handle_radarr_failure(item):
    print(f"Handling failure for {item['title']} (Movie ID: {item['movieId']})")

    response = requests.delete(
        f"{RADARR_URL}/queue/{item['id']}?removeFromClient=false&blocklist=true&skipRedownload=false&changeCategory=false",
        headers={"X-Api-Key": RADARR_API_KEY}
    )
    print(f"Queue removal response: {response.status_code}, {response.text}")


# Function to handle failed items in Sonarr
def handle_sonarr_failure(item):
    print(f"Handling failure for {item['title']} (Series ID: {item['seriesId']})")

    response = requests.delete(
        f"{SONARR_URL}/queue/{item['id']}?removeFromClient=false&blocklist=true&skipRedownload=false&changeCategory=false",
        headers={"X-Api-Key": SONARR_API_KEY}
    )
    print(f"Queue removal response: {response.status_code}, {response.text}")


# Process Radarr queue
radarr_failed = False
for item in get_radarr_queue():
    if item.get('status') == "completed" and item.get('trackedDownloadStatus') in ERROR_STATUSES:
        radarr_failed = True
        handle_radarr_failure(item)

# Process Sonarr queue
sonarr_failed = False
for item in get_sonarr_queue():
    if item.get('status') == "completed" and item.get('trackedDownloadStatus') in ERROR_STATUSES:
        sonarr_failed = True
        handle_sonarr_failure(item)

# If no failures were handled, print confirmation
if not radarr_failed and not sonarr_failed:
    print("Everything looks good! Nothing to see here.")

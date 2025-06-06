# Radarr & Sonarr Auto-Blacklist & Re-Search Script

## Overview

This Python script interacts with the **Radarr** and **Sonarr** APIs to:
- **Check** the download queue for failed items.
- **Blacklist** problematic downloads.
- **Trigger a re-search** for alternative releases.
- **Ensure items are correctly removed from the queue** without affecting the download client.

This helps automate the management of movie and TV show downloads, improving reliability.

## Features
✅ Scans **Radarr & Sonarr** queues for completed downloads with errors.  
✅ Removes failed downloads while **keeping the original category intact**.  
✅ Adds releases to the **blocklist** to prevent repeat failures.  
✅ Allows Radarr & Sonarr to **re-search** for alternate sources.    

## Requirements

- **Python 3.x**
- Installed **Radarr** and/or **Sonarr** (with API access enabled).
- Dependencies: `requests` (install via `pip install requests`)

## Configuration

1. **Edit the script** to add your Radarr and Sonarr API keys:
   ```python
   RADARR_API_KEY = "your_radarr_api_key"
   SONARR_API_KEY = "your_sonarr_api_key"
   RADARR_URL = "http://localhost:7878/api/v3"
   SONARR_URL = "http://localhost:8989/api/v3"
   ```

2. **Run the script**:
   ```bash
   python blocklistarr.py
   ```
   
## How It Works

The script does the following:
1. Requests the **queue status** from Radarr and Sonarr.
2. Identifies **failed downloads** based on `status` and `trackedDownloadStatus`.
3. Removes items **from the queue** but does **not** remove them from the download client.
4. Adds the failed item to the **blocklist**.
5. Initiates a **search command** to find a better alternative.

If no errors are found, the script prints:
```
Everything looks good! Nothing to see here.
```

## License
MIT License

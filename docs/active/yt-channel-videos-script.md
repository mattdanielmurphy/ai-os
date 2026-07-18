# YouTube Channel Videos Downloader Script

**Location:** `scripts/yt-channel-videos.py`

## Purpose
This script automates the process of fetching a complete list of videos uploaded by a specific YouTube channel. It bypasses the need for complex web scraping by leveraging the official YouTube Data API v3. 

## How it Works
It uses a two-step process:
1. **Channel to Playlist Translation:** YouTube channels don't expose their entire video list as a single queryable endpoint. However, every channel has a hidden auto-generated "Uploads" playlist. The script hits the `channels` API endpoint (`part=contentDetails`) with the given channel handle to retrieve this specific `uploads` playlist ID (which is identical to the Channel ID, but starts with `UU` instead of `UC`).
2. **Playlist Pagination:** Once the `uploads` playlist ID is obtained, the script queries the `playlistItems` endpoint (`part=snippet`). Since API limits return a maximum of 50 items per request, the script implements a `while` loop to follow the `nextPageToken` continuously until every video in the channel has been retrieved.

## Usage
The script is executable and accepts a few useful arguments:

```bash
# Print all videos to the terminal
./yt-channel-videos.py JaredOwen

# Save the output to a standard text file
./yt-channel-videos.py JaredOwen -o jared_owen_videos.txt

# Save the output to a CSV file (perfect for importing into Google Sheets)
./yt-channel-videos.py JaredOwen --csv -o jared_owen_videos.csv
```

## Maintenance & Context
- **Dependencies:** The script was purposefully written using only standard Python libraries (`urllib`, `json`, `argparse`) so it requires zero setup or `pip install` commands.
- **API Key:** The script currently contains a hardcoded API key that has YouTube Data API v3 enabled. If it ever stops working, it is likely because the quota on this key has been exhausted or the key was revoked. You can replace it with a new key from the Google Cloud Console.

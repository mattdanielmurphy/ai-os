#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import argparse
import sys

API_KEY = "AIzaSyBB3I_M7knApTmO6rVrzrV0cumPbSHFBbs"

def get_channel_uploads_playlist(handle):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={urllib.parse.quote(handle)}&key={API_KEY}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if not data.get("items"):
                print(f"Error: Could not find channel with handle {handle}", file=sys.stderr)
                sys.exit(1)
            
            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching channel details: {e}", file=sys.stderr)
        sys.exit(1)

def get_playlist_videos(playlist_id):
    videos = []
    page_token = ""
    
    while True:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={API_KEY}"
        if page_token:
            url += f"&pageToken={page_token}"
            
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    video_id = snippet.get("resourceId", {}).get("videoId")
                    title = snippet.get("title")
                    published_at = snippet.get("publishedAt")
                    if video_id:
                        videos.append({
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "published_at": published_at
                        })
                
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
        except Exception as e:
            print(f"Error fetching playlist videos: {e}", file=sys.stderr)
            break
            
    return videos

def main():
    parser = argparse.ArgumentParser(description="Download a list of all videos from a YouTube channel")
    parser.add_argument("handle", help="The YouTube channel handle (e.g. JaredOwen)")
    parser.add_argument("-o", "--output", help="Output file (e.g. videos.txt, videos.csv)")
    parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    args = parser.parse_args()
    
    handle = args.handle
    if handle.startswith("@"):
        handle = handle[1:]
        
    print(f"Fetching details for channel @{handle}...")
    uploads_id = get_channel_uploads_playlist(handle)
    print(f"Found uploads playlist: {uploads_id}")
    
    print("Fetching videos...")
    videos = get_playlist_videos(uploads_id)
    print(f"Total videos found: {len(videos)}")
    
    output_lines = []
    if args.csv:
        output_lines.append("Title,URL,PublishedAt")
        for v in videos:
            title = v['title'].replace('"', '""')
            output_lines.append(f'"{title}","{v["url"]}","{v["published_at"]}"')
    else:
        for v in videos:
            output_lines.append(f"{v['title']}\n{v['url']}\n{v['published_at']}\n")
            
    output_text = "\n".join(output_lines)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Saved to {args.output}")
    else:
        print("\n--- Videos ---")
        print(output_text)

if __name__ == "__main__":
    main()

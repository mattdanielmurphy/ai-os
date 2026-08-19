---
title: "Remove Duplicate Media Clips"
date: "2026-08-03"
conversation_id: "de1a0a2b-3c25-4a2d-ad19-6c0bea897df1"
source: "antigravity"
---

# Remove Duplicate Media Clips

## User

Update `slice_media.py` in `/Users/matt/projects/bumblebee` to prevent duplicate clips.
The `.srt` file has consecutive identical subtitles.
In the loop in `slice_media.py`:
1. Add a variable before the loop: `prev_sig = None`
2. Inside the loop, after calculating `clean_content`, `start_time`, and `end_time`:
```python
        sig = (start_time, end_time, clean_content)
        if sig == prev_sig:
            continue
        prev_sig = sig
```
Make sure to use `replace_file_content` accurately.

Then, create a new file `/Users/matt/projects/bumblebee/fix_clips.py` using `write_to_file`.
It should do the following:
1. Load `manifest.json`.
2. Iterate through the manifest list.
3. Keep track of the `prev_transcript`.
4. If a clip's `transcript` is exactly the same as the previous clip's `transcript` (consecutive duplicate):
   - Delete the `.wav` file associated with it (`os.remove(item['file'])`).
5. Otherwise, keep it and update `prev_transcript`.
6. Save the filtered list back to `manifest.json`.
7. Print a summary (e.g., "Kept X clips out of Y").

Do not spawn other subagents.

---

## Assistant

Created At: 2026-08-02T22:12:06-06:00
Completed At: 2026-08-02T22:12:06-06:00
{"name":".DS_Store","sizeBytes":"6148"}
{"name":"chat_assemble.py","sizeBytes":"1882"}
{"name":"clips","isDir":true}
{"name":"media","isDir":true}
{"name":"slice_media.py","sizeBytes":"1358"}
{"name":"venv","isDir":true}

Summary: This directory contains 3 subdirectories and 3 files.

Created At: 2026-08-02T22:12:06-06:00
Completed At: 2026-08-02T22:12:06-06:00
File Path: `file:///Users/matt/projects/bumblebee/slice_media.py`
Total Lines: 55
Total Bytes: 1358
Showing lines 1 to 55
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import pysrt
2: import os
3: import subprocess
4: import json
5: import re
6: 
7: def clean_text(text):
8:     text = re.sub(r'<[^>]+>', '', text)
9:     text = text.replace('\n', ' ')
10:     return text.strip()
11: 
12: def slice_media():
13:     srt_file = 'media/louis.srt'
14:     video_file = 'media/louis.mp4'
15:     clips_dir = 'clips'
16:     
17:     if not os.path.exists(clips_dir):
18:         os.makedirs(clips_dir)
19:         
20:     subs = pysrt.open(srt_file)
21:     manifest = []
22:     
23:     for i, sub in enumerate(subs, 1):
24:         clean_content = clean_text(sub.text)
25:         if not clean_content:
26:             continue
27:             
28:         start_time = max(0, (sub.start.ordinal / 1000.0) - 0.1)
29:         end_time = (sub.end.ordinal / 1000.0) + 0.1
30:         
31:         file_name = f'clips/clip_{i:04d}.wav'
32:         
33:         cmd = [
34:             'ffmpeg', '-y', '-i', video_file,
35:             '-ss', str(start_time),
36:             '-to', str(end_time),
37:             '-ar', '16000', '-ac', '1',
38:             file_name
39:         ]
40:         
41:         print(f"Generating {file_name}...")
42:         subprocess.run(cmd, capture_output=True)
43:         
44:         manifest.append({
45:             "id": f"clip_{i:04d}",
46:             "file": file_name,
47:             "transcript": clean_content
48:         })
49:         
50:     with open('manifest.json', 'w') as f:
51:         json.dump(manifest, f, indent=2)
52: 
53: if __name__ == '__main__':
54:     slice_media()
55: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-02T22:12:08-06:00
Completed At: 2026-08-02T22:12:08-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/bumblebee/slice_media.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -20,6 +20,7 @@
     subs = pysrt.open(srt_file)
     manifest = []
     
+    prev_sig = None
     for i, sub in enumerate(subs, 1):
         clean_content = clean_text(sub.text)
         if not clean_content:
@@ -26,6 +26,11 @@
-            
+
         start_time = max(0, (sub.start.ordinal / 1000.0) - 0.1)
         end_time = (sub.end.ordinal / 1000.0) + 0.1
+
+        sig = (start_time, end_time, clean_content)
+        if sig == prev_sig:
+            continue
+        prev_sig = sig
         
         file_name = f'clips/clip_{i:04d}.wav'
         
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-02T22:12:11-06:00
Completed At: 2026-08-02T22:12:11-06:00
Created file file:///Users/matt/projects/bumblebee/fix_clips.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-02T22:12:12-06:00
Completed At: 2026-08-02T22:12:12-06:00
Message sent to "aced1e5f-07c3-4b14-b13a-5c3b8d71bb7c".

Finished updating `slice_media.py` and creating `fix_clips.py`.

---

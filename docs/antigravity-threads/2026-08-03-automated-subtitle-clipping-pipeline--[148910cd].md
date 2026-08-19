---
title: "Automated Subtitle Clipping Pipeline"
date: "2026-08-03"
conversation_id: "148910cd-3dd7-480b-90d7-8279276c2725"
source: "antigravity"
---

# Automated Subtitle Clipping Pipeline

## User

Write two Python scripts in `/Users/matt/projects/bumblebee`.

1. `slice_media.py`:
- Use `pysrt` to read `media/louis.srt`.
- Create a directory `clips` if it doesn't exist.
- Loop over the subtitles.
- Strip HTML tags (e.g., `<i>`, `<b>`) and replace newlines with spaces to get clean text.
- Calculate start and end times in seconds (e.g., `sub.start.ordinal / 1000.0`).
- Add 100ms padding: `start_time = max(0, start_time - 0.1)`, `end_time = end_time + 0.1`.
- Use `subprocess.run` to call `ffmpeg`:
  `ffmpeg -y -i media/louis.mp4 -ss {start_time} -to {end_time} -ar 16000 -ac 1 clips/clip_{index:04d}.wav`
- Save a dictionary mapping ID to text in a list, and write it to `manifest.json`:
  `[{"id": "clip_0001", "file": "clips/clip_0001.wav", "transcript": "text..."}, ...]`

2. `chat_assemble.py`:
- Load `manifest.json`.
- Accept a prompt via `sys.argv[1]` or use "Tell me about your typical day." as default.
- Pick 3 random transcripts from `manifest.json` that are at least 5 words long.
- Use `litellm.completion` to call the LLM:
  `model="deepseek/v4-flash-nitro"`
  `messages=[{"role": "user", "content": f"Answer the following prompt: '{prompt}'. You MUST incorporate the following exact phrases seamlessly into your response:\n{phrases}"}]`
- Get the LLM response text.
- Split the text into chunks using regex on punctuation (e.g. `re.split(r'[,.?!]+', response_text)`).
- For each chunk (if it has alphanumeric chars):
  - Use `thefuzz.process.extractOne(chunk, {item['file']: item['transcript'] for item in manifest})` to find the best matching clip.
- Collect the ordered list of `clip_xxxx.wav` files.
- Write a `concat_list.txt` formatted for ffmpeg: `file 'clips/clip_xxxx.wav'` on each line.
- Use `subprocess.run` to concatenate them: `ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.wav -y`.
- Play the result: `subprocess.run(["afplay", "output.wav"])`.
- Print out the LLM's full text and the chosen clips so the user can see what was selected.

Use `write_to_file` to create both scripts. No need for complex error handling, just a clean MVP.

---

## Assistant

Created At: 2026-08-02T21:38:43-06:00
Completed At: 2026-08-02T21:38:43-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-02T21:38:45-06:00
Completed At: 2026-08-02T21:38:45-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-02T21:38:46-06:00
Completed At: 2026-08-02T21:38:46-06:00
Message sent to "aced1e5f-07c3-4b14-b13a-5c3b8d71bb7c".

Finished creating `slice_media.py` and `chat_assemble.py` in `/Users/matt/projects/bumblebee`.

---

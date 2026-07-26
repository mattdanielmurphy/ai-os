# MKV Audio Track Alignment & Replacement Guide

This guide documents the process of replacing an incorrect or dubbed audio track in an MKV video with a clean, high-quality external audio track (such as one downloaded via `yt-dlp`), and aligning them precisely when they differ in duration or starting silence.

## Problem Statement

An MKV video file has multiple audio tracks (e.g., a Russian dub and a fake English track that is actually just the Russian dub again). We download a high-quality, clean English audio track from YouTube, but it has a different length and starting silence offset than the video's audio tracks. 

To replace the incorrect track, we must find the precise sub-second offset to align the new track with the video and original audio.

---

## The Workflow

### 1. Extract and Analyze Audio Onsets

To find where the audio starts, convert the first 30 seconds of both files to 8000 Hz, mono WAV files and locate the first non-silent sample in each.

```bash
# Extract first 30 seconds of reference audio (Track 1) from the MKV
ffmpeg -y -i input.mkv -map 0:a:0 -ss 0 -t 30 -ar 8000 -ac 1 /tmp/ref.wav

# Extract first 30 seconds of the new high-quality audio
ffmpeg -y -i input.mp3 -ss 0 -t 30 -ar 8000 -ac 1 /tmp/new.wav
```

Run a lightweight Python script to find the first significant sample (using a threshold of 2% of the maximum amplitude):

```python
import wave, struct

def find_onset(path, threshold_ratio=0.02):
    with wave.open(path, 'rb') as w:
        frames = w.getnframes()
        data = struct.unpack(f'<{frames}h', w.readframes(frames))
        rate = w.getframerate()
        max_val = max(abs(x) for x in data)
        threshold = max_val * threshold_ratio
        for idx, val in enumerate(data):
            if abs(val) > threshold:
                return idx / rate

print("Reference Onset:", find_onset('/tmp/ref.wav'))
print("New Audio Onset:", find_onset('/tmp/new.wav'))
```

*Example Results:*
* Reference Onset: `1.0285` seconds
* New Audio Onset: `0.4400` seconds
* **Calculated Offset Delay:** `1.0285 - 0.4400 = 0.5885` seconds (~588ms).

---

### 2. Validate with Envelope Cross-Correlation (Optional but Recommended)

Because voice dubs often completely alter speech waveforms, a direct sample-by-sample cross-correlation of the raw waveforms can fail or yield low correlation. 

Instead, calculate the **volume envelope** (RMS values over 100ms windows) and cross-correlate those envelopes. The background music, sound effects, and general sound pacing will align perfectly, regardless of the vocal differences:

```python
import wave, struct

def get_envelope(path, win_ms=100):
    with wave.open(path, 'rb') as w:
        data = struct.unpack(f'<{w.getnframes()}h', w.readframes(w.getnframes()))
        rate = w.getframerate()
        win_size = int(rate * win_ms / 1000)
        chunks = [data[i:i+win_size] for i in range(0, len(data), win_size)]
        return [int((sum(x*x for x in c)/len(c))**0.5) if c else 0 for c in chunks]

# 1. Load envelopes
env_ref = get_envelope('/tmp/ref.wav')
env_new = get_envelope('/tmp/new.wav')

# 2. Extract a window in the middle of reference (5s to 25s) and normalize
w_start, w_end = 50, 250
w = env_ref[w_start:w_end]
m_w = sum(w)/len(w)
w_norm = [(x - m_w) / (((sum((y - m_w)**2 for y in w)/len(w))**0.5) or 1) for x in w]

# 3. Normalize new audio envelope
m_new = sum(env_new)/len(env_new)
new_norm = [(x - m_new) / (((sum((y - m_new)**2 for y in env_new)/len(env_new))**0.5) or 1) for x in env_new]

# 4. Search offsets (-5.0s to +5.0s)
best_offset_idx, best_corr = 0, -1.0
for offset in range(-50, 51):
    s2_start = w_start + offset
    s2_end = w_end + offset
    if s2_start >= 0 and s2_end <= len(new_norm):
        corr = sum(a*b for a, b in zip(w_norm, new_norm[s2_start:s2_end])) / len(w_norm)
        if corr > best_corr:
            best_corr, best_offset_idx = corr, offset

print(f"Peak Correlation: {best_corr:.4f} at offset {best_offset_idx * 0.1:+.3f}s")
```

If the calculated offset delay (e.g. `0.588s`) matches the peak envelope correlation (e.g. `-0.6s`), the alignment is highly precise.

---

### 3. Replace and Delay Track with FFmpeg

Once the offset is known, use `ffmpeg` to merge the streams. We apply the `adelay` filter complex to delay the new audio track (e.g., delaying by 588ms) and map the streams appropriately.

Using stream copying (`-c:v copy` and `-c:a:0 copy`) ensures that the video and reference tracks are preserved exactly as they are without transcoding, completing the entire operation in seconds.

```bash
ffmpeg -y -i input.mkv -i input.mp3 \
       -filter_complex "[1:a]adelay=588|588[eng_aligned]" \
       -map 0:v:0 \
       -map 0:a:0 \
       -map "[eng_aligned]" \
       -map 0:s \
       -c:v copy \
       -c:a:0 copy \
       -c:a:1 ac3 -b:a:1 192k \
       -c:s copy \
       -metadata:s:a:1 language=eng \
       -metadata:s:a:1 title="Original @ DD 2.0" \
       output_fixed.mkv
```

#### Parameter Breakdown:
* `-filter_complex "[1:a]adelay=588|588[eng_aligned]"`: Delays both left and right channels of Input 1 (the MP3) by 588ms.
* `-map 0:v:0`: Maps the video from the MKV as the first stream.
* `-map 0:a:0`: Maps the first audio track (Russian) from the MKV.
* `-map "[eng_aligned]"`: Maps the newly aligned English track.
* `-map 0:s`: Maps all subtitle tracks from the original MKV.
* `-c:a:1 ac3 -b:a:1 192k`: Transcodes the delayed English track to Dolby Digital AC3 format at 192kbps.
* `-metadata:s:a:1 language=eng -metadata:s:a:1 title="..."`: Restores the language code and name of the English track.

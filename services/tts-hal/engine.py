#!/usr/bin/env python3
"""
services/tts-hal/engine.py
HAL-9000 Voice Synthesis Engine with Studio Acoustic DSP.

Douglas Rain's HAL-9000 vocal signature:
- Measured, calm cadence (~135-145 wpm)
- Flat, monotone pitch with minimal emotional inflection
- Studio acoustic bandpass filtering (200 Hz high-pass to 4200 Hz low-pass)
- Mild dynamic range compression (intercom / radio console sound)
"""

import os
import sys
import tempfile
import subprocess
import re
from pathlib import Path
from typing import Optional

try:
    import numpy as np
    import soundfile as sf
    from scipy import signal
    HAS_AUDIO_DSP = True
except ImportError:
    HAS_AUDIO_DSP = False


class HalVoiceEngine:
    """HAL-9000 Voice Synthesizer & DSP Processor."""

    def __init__(self, voice_name: str = "Daniel", rate: int = 140):
        self.voice_name = voice_name
        self.rate = rate  # 135-145 wpm gives HAL's calm, deliberate cadence
        self.cache_dir = Path.home() / ".ai-os" / "cache" / "hal_tts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_text(self, text: str) -> str:
        """Sanitizes text for speech synthesis, stripping code and markdown."""
        t = text.strip()
        # Strip code blocks
        t = re.sub(r"```[\s\S]*?```", "", t)
        # Strip inline code
        t = re.sub(r"`([^`]+)`", r"\1", t)
        # Strip URLs
        t = re.sub(r"https?://\S+", "", t)
        # Strip markdown links [text](url) -> text
        t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
        # Strip bold/italic markers
        t = re.sub(r"[*_~]{1,3}", "", t)
        # Strip headings
        t = re.sub(r"^#+\s*", "", t, flags=re.MULTILINE)
        # Strip HTML tags
        t = re.sub(r"<[^>]+>", "", t)
        # Verbalize common symbols
        t = t.replace("%", " percent ")
        t = t.replace("&", " and ")
        t = t.replace("=", " equals ")
        t = t.replace("+", " plus ")
        t = t.replace("±", " plus or minus ")
        # Clean extra whitespace
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def apply_hal_dsp(self, input_wav: Path, output_wav: Path):
        """Applies HAL-9000 bandpass filtering, mild compression, and normalization."""
        if not HAS_AUDIO_DSP:
            # If scipy/numpy not loaded, copy directly
            import shutil
            shutil.copyfile(input_wav, output_wav)
            return

        try:
            data, sr = sf.read(str(input_wav))
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            # 1. Bandpass filter: 200 Hz to 4200 Hz (4th-order Butterworth)
            nyquist = 0.5 * sr
            lowcut = max(20.0, 200.0 / nyquist)
            highcut = min(0.95, 4200.0 / nyquist)
            
            b, a = signal.butter(4, [lowcut, highcut], btype="band")
            filtered = signal.filtfilt(b, a, data)

            # 2. Dynamic Range Compression (soft knee emulation)
            # Threshold: -16 dBFS (~0.15), Ratio: 3:1
            threshold = 0.15
            ratio = 3.0
            abs_sig = np.abs(filtered)
            compressed = np.where(
                abs_sig > threshold,
                np.sign(filtered) * (threshold + (abs_sig - threshold) / ratio),
                filtered
            )

            # 3. Peak normalization to -1.5 dB (~0.84)
            peak = np.max(np.abs(compressed))
            if peak > 0:
                normalized = (compressed / peak) * 0.84
            else:
                normalized = compressed

            sf.write(str(output_wav), normalized, sr, subtype="PCM_16")
        except Exception as e:
            # Fallback to direct copy on processing failure
            import shutil
            shutil.copyfile(input_wav, output_wav)

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> Path:
        """Synthesizes text into a HAL-9000 styled WAV file."""
        clean_text = self.sanitize_text(text)
        if not clean_text:
            clean_text = "I am unable to process that."

        if output_path is None:
            tmp_handle, tmp_path_str = tempfile.mkstemp(suffix=".wav", prefix="hal_")
            os.close(tmp_handle)
            final_wav = Path(tmp_path_str)
        else:
            final_wav = output_path

        raw_aiff = final_wav.with_suffix(".raw.aiff")

        try:
            # 1. Synthesize using macOS `say` with Douglas Rain-like voice (Daniel - UK/Transatlantic, calm)
            cmd = [
                "say",
                "-v", self.voice_name,
                "-r", str(self.rate),
                "-o", str(raw_aiff),
                clean_text
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 2. Apply HAL-9000 DSP Filter
            self.apply_hal_dsp(raw_aiff, final_wav)

        finally:
            if raw_aiff.exists():
                try:
                    raw_aiff.unlink()
                except Exception:
                    pass

        return final_wav


if __name__ == "__main__":
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
    else:
        phrase = "Good morning, Dave. Everything is functioning normally."

    engine = HalVoiceEngine()
    out = engine.synthesize(phrase)
    print(f"Generated HAL audio: {out}")

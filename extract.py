import os
import subprocess
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel

"""
extract.py
-----------

This script automates the process of extracting highlight clips from a video based on keyword detection in the transcript. It uses the faster-whisper model for transcription and ffmpeg for video processing.

Features:
- Transcribes the input video using Whisper.
- Scans the transcript for specified keywords (e.g., laughter, hype words).
- Exports highlight clips around detected keywords, ensuring a minimum duration and configurable buffer before/after the moment.
- Saves the transcript and all clips to disk.
- Parallelizes clip export for speed.

Configuration:
- Set the video file, output directories, keywords, model/device, and export parameters in the CONFIG section.

Dependencies:
- faster-whisper
- ffmpeg (must be installed and available in PATH)

Usage:
    python extract.py

Outputs:
- transcript.txt: Full transcript of the video with timestamps.
- clips/: Directory containing highlight video clips.
"""

# ----------------- CONFIG -----------------
video_path = "your_video.mkv"  # <-- change to your actual video file
output_transcript = "transcript.txt"
clip_output_dir = "clips"
keywords = [
    "lol",
    "laugh",
    "anjing",
    "anying",
    "goblog",
    "kontol",
    "memek",
    "hahaha",
    "screamed",
    "goblok",
    "aduh",
    "ardi",
    "beni",
    "gendut",
    "botak"
]
model_size = "medium"  # or 'small', 'large-v2' for better accuracy
device = "cuda"  # 'cuda' for GPU, 'cpu' otherwise
compute_type = "float16"  # float16 = faster on GPU
max_workers = 6  # threads for parallel clip exports
buffer_before = 1.5  # seconds before detected moment
buffer_after = 3.0  # seconds after detected moment
min_duration = 60  # minimum clip length in seconds
fps = "60"  # clip frame rate

# ----------------- START -----------------
total_start = time.time()

print(f"🔥 Loading Whisper model ({model_size}) on {device} with {compute_type}...")
model = WhisperModel(model_size, device=device, compute_type=compute_type)

# Transcribe
print(f"🎥 Transcribing video: {video_path}")
transcribe_start = time.time()

segments, info = model.transcribe(
    video_path,
    language=None,  # Let it auto-detect (better for mixed speech)
    beam_size=5,
    vad_filter=True,
)

transcribe_end = time.time()
print(f"✅ Transcription done in {transcribe_end - transcribe_start:.2f}s")

# Save transcript + scan for keywords
print("📝 Saving transcript and scanning for keywords...")
os.makedirs(clip_output_dir, exist_ok=True)

highlight_times: List[Tuple[float, float]] = []
with open(output_transcript, "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments):
        start = segment.start
        end = segment.end
        text = segment.text

        f.write(f"{start:.2f} --> {end:.2f}: {text}\n")

        percent = ((i + 1) / info.duration) * 100
        print(f"⌛ Progress: {percent:.2f}% — {text.strip()[:40]}", end="\r")

        if any(kw in text.lower() for kw in keywords):
            highlight_times.append((start, end))

print(f"\n🎉 Found {len(highlight_times)} funny/hype moments")


# ----------------- EXPORT CLIPS -----------------
def export_clip(i: int, start: float, end: float):
    """
    Export a video clip centered around the detected moment.

    Args:
        i (int): Index of the clip (for naming).
        start (float): Start time of the detected segment (seconds).
        end (float): End time of the detected segment (seconds).
    """
    clip_name = f"clip_{i+1}.mkv"
    output_path = os.path.join(clip_output_dir, clip_name)

    # Minimum 60s duration, centered on the moment
    duration = max((end - start) + buffer_after, min_duration)
    clip_start = max(0, (start + end) / 2 - duration / 2)

    subprocess.run(
        [
            "ffmpeg",
            "-ss",
            str(clip_start),
            "-i",
            video_path,
            "-t",
            str(duration),
            "-r",
            fps,
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p4",
            "-cq",
            "21",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            output_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"✅ Exported: {clip_name}")


clip_start_time = time.time()
print("🚀 Exporting clips...")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i, (start, end) in enumerate(highlight_times):
        executor.submit(export_clip, i, start, end)

clip_end_time = time.time()

print(f"🏁 Exported all clips in {clip_end_time - clip_start_time:.2f}s")
print(f"📄 Transcript saved as {output_transcript}")
print(f"📂 Clips saved in: {clip_output_dir}")

total_end = time.time()
print(
    f"🔥 TOTAL RUNTIME: {(total_end - total_start):.2f}s ({(total_end - total_start)/60:.2f} mins)"
)

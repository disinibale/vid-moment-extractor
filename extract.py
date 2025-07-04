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
- Scans the transcript for specified keywords.
- Merges nearby keyword moments to create consolidated clips.
- Exports highlight clips with configurable buffers and duration.
- Catches and reports errors during video export.
- Parallelizes clip export for speed.

Configuration:
- Set the video file, output directories, keywords, model/device, and export parameters in the CONFIG section.

Dependencies:
- faster-whisper
- ffmpeg (must be installed and available in PATH)

Usage:
    python extract.py
"""

# ----------------- CONFIG -----------------
video_path = "your_video.mkv"  # <-- Path to your video file
output_transcript = "transcript.txt" # <-- Name for the output transcript file
clip_output_dir = "clips"      # <-- Folder to save the final clips

# Keywords to search for in the transcript. Case-insensitive.
keywords = [
    "lol", "laugh", "anjing", "anying", "goblog", "kontol",
    "memek", "hahaha", "screamed", "goblok", "aduh", "ardi",
    "beni", "gendut", "botak"
]

# --- AI & Performance Settings ---
model_size = "medium"       # Whisper model size ('tiny', 'base', 'small', 'medium', 'large-v3')
device = "cuda"             # 'cuda' for GPU (NVIDIA), 'cpu' for CPU
compute_type = "float16"    # 'float16' for faster GPU processing, 'int8' or 'float32' for CPU
max_workers = 6             # Number of clips to export in parallel. Adjust based on your CPU cores.

# --- Clip Timing & Quality Settings ---
buffer_before = 1.5         # Seconds to include before the keyword is spoken
buffer_after = 3.0          # Seconds to include after the keyword is spoken
min_duration = 60           # Minimum total duration for any clip (in seconds)
merge_threshold = 10        # Max seconds between moments to merge them into one clip
fps = "60"                  # Frame rate for the output clips
video_codec = "h264_nvenc"  # FFMPEG video encoder. Use 'libx264' for CPU.

# ----------------- START -----------------
total_start = time.time()

print(f"🔥 Loading Whisper model ({model_size}) on {device} with {compute_type}...")
model = WhisperModel(model_size, device=device, compute_type=compute_type)

# Transcribe
print(f"🎥 Transcribing video: {video_path}")
transcribe_start = time.time()

segments, info = model.transcribe(
    video_path,
    language=None,
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
        start, end, text = segment.start, segment.end, segment.text
        f.write(f"[{start:.2f}s -> {end:.2f}s] {text}\n")

        # Simple progress bar
        percent_done = (end / info.duration) * 100
        print(f"⌛ Progress: {percent_done:.2f}%", end="\r")

        if any(kw in text.lower() for kw in keywords):
            highlight_times.append((start, end))

print(f"\n🎉 Found {len(highlight_times)} raw keyword moments.")


# ----------------- MERGE MOMENTS -----------------
def merge_overlapping_moments(moments: List[Tuple[float, float]], threshold: float) -> List[Tuple[float, float]]:
    """Merges moments that are close to each other."""
    if not moments:
        return []

    # Sort moments by start time
    sorted_moments = sorted(moments, key=lambda x: x[0])
    
    merged = [sorted_moments[0]]
    for current_start, current_end in sorted_moments[1:]:
        last_start, last_end = merged[-1]

        # If the current moment is within the threshold of the last one, merge them
        if current_start <= last_end + threshold:
            merged[-1] = (last_start, max(last_end, current_end))
        else:
            merged.append((current_start, current_end))
            
    return merged

print(f"🤝 Merging moments within {merge_threshold}s of each other...")
merged_times = merge_overlapping_moments(highlight_times, merge_threshold)
print(f"✨ Total clips to be exported: {len(merged_times)}")


# ----------------- EXPORT CLIPS -----------------
def export_clip(i: int, start: float, end: float):
    """
    Export a video clip centered around the detected moment with error handling.
    """
    clip_name = f"clip_{i+1}.mkv"
    output_path = os.path.join(clip_output_dir, clip_name)

    # Calculate the clip's start and duration
    moment_center = (start + end) / 2
    clip_duration = max((end - start) + buffer_before + buffer_after, min_duration)
    clip_start = max(0, moment_center - (clip_duration / 2))

    command = [
        "ffmpeg",
        "-ss", str(clip_start),
        "-i", video_path,
        "-t", str(clip_duration),
        "-r", fps,
        "-c:v", video_codec,
        "-preset", "p4",
        "-cq", "21",
        "-c:a", "aac",
        "-b:a", "192k",
        "-y", # Overwrite output file if it exists
        output_path,
    ]

    try:
        result = subprocess.run(
            command,
            check=True, # Raise an exception if ffmpeg returns a non-zero exit code
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE, # Capture stderr to show on error
            encoding='utf-8'
        )
        print(f"✅ Exported: {clip_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR exporting {clip_name}: FFMPEG failed.")
        print(f"    Command: {' '.join(command)}")
        print(f"    FFMPEG stderr:\n{e.stderr}")


clip_start_time = time.time()
print("🚀 Exporting clips...")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    for i, (start, end) in enumerate(merged_times):
        executor.submit(export_clip, i, start, end)

clip_end_time = time.time()

print(f"🏁 Exported all clips in {clip_end_time - clip_start_time:.2f}s")
print(f"📄 Transcript saved as {output_transcript}")
print(f"📂 Clips saved in: {clip_output_dir}")

total_end = time.time()
print(
    f"🔥 TOTAL RUNTIME: {(total_end - total_start):.2f}s ({(total_end - total_start)/60:.2f} mins)"
)

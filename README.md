# 🎮 Vid Moment Extractor

Automatically find and clip hype moments from your videos using AI transcription.

This script uses the power of `faster-whisper` to generate a timestamped transcript of your video, then automatically scans it for keywords you define (like "hahaha", "omg", or any inside joke). It then uses `ffmpeg` to rapidly export all those moments into individual clips, ready for sharing.

---

## ✨ Core Features

| Icon | Feature | Description |
| :--: | --------------------------- | ------------------------------------------------------------------------------------------------- |
| `🚀` | **GPU-Accelerated Transcription** | Uses `faster-whisper` with CUDA (`float16`) for blazing-fast speech-to-text on NVIDIA GPUs. |
| `🎯` | **Custom Keyword Detection** | Define your own list of hype/funny words to trigger a clip. |
| `🤝` | **Intelligent Moment Merging** | Automatically combines nearby keyword moments into a single, longer clip to avoid redundancy. |
| `✂️` | **Automated Clipping** | Exports video segments with configurable time buffers and a minimum duration. |
| `🧵` | **Parallel Exporting** | Leverages `ThreadPoolExecutor` to export multiple clips at the same time, saving you hours. |
| `💻` | **Hardware Encoding** | Defaults to `h264_nvenc` for efficient video encoding on NVIDIA GPUs, offloading work from the CPU. |
| `⚠️` | **Error Reporting** | Catches and reports any errors from `ffmpeg` during the export process. |

---

## ⚙️ How It Works

The script follows a simple pipeline to get from a full video to a folder of clips:

`▶️ Video File` ➔ `🧠 faster-whisper` ➔ `📝 Transcript` ➔ `🔍 Keyword Scan` ➔ `🤝 Merge Moments` ➔ `🚀 Parallel Jobs` ➔ `🎬 FFMPEG Clips`

1.  **Transcription**: `faster-whisper` processes the entire video and generates a highly accurate transcript with word-level timestamps.
2.  **Keyword Scan**: The script reads the transcript and identifies every instance of your chosen keywords.
3.  **Moment Merging**: The script intelligently combines keyword timestamps that are close to each other, preventing dozens of short, overlapping clips.
4.  **Clipping**: For each final moment, `ffmpeg` is used to export a clip. The duration and start/end time buffers are fully configurable.
5.  **Parallel Processing**: Multiple `ffmpeg` jobs run in parallel to export clips simultaneously, dramatically speeding up the process.

---

## 🚀 Getting Started

### 1. Prerequisites

-   **Python 3.8+**
-   **FFmpeg**: You must have `ffmpeg` installed and accessible in your system's PATH. You can download it from [ffmpeg.org](https://ffmpeg.org/download.html).

### 2. Installation

Clone this repository and install the required Python package:

```bash
pip install faster-whisper
```

### 3. Configuration

Open `extract.py` in a text editor. All the settings you need to change are in the `CONFIG` section at the top of the file.

See the **Configuration** section below for a detailed explanation of each option.

### 4. Run the Script

Once configured, run the script from your terminal:

```bash
python extract.py
```

The script will print its progress as it transcribes the video and exports the clips.

---

## 🛠️ Configuration

All settings are located in the `CONFIG` section at the top of `extract.py`.

```python
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
```

---

## 📦 Output

After the script finishes, you will find:

-   📄 **`transcript.txt`**: The full, timestamped transcript of your video.
-   📁 **`clips/`**: A folder containing all the extracted highlight clips, named `clip_1.mkv`, `clip_2.mkv`, etc.

---

## 💡 Troubleshooting & Tips

> **😟 Getting FFMPEG or Encoder Errors?**
>
> The script now has built-in error reporting for `ffmpeg`. If you see an error, the most common cause is an incompatible `video_codec`.
>
> -   **For NVIDIA GPUs**: The default `h264_nvenc` is recommended.
> -   **For AMD GPUs or CPU-only**: Change `video_codec` to `"libx264"` in the configuration. This is a high-quality software encoder that is universally compatible.

> **🤔 CUDA / GPU Errors or Slow Performance?**
>
> -   If you don't have a compatible NVIDIA GPU, make sure to set `device = "cpu"` in the configuration.
> -   When using the CPU, you should also change `compute_type` to `"float32"` or `"int8"` for better performance.
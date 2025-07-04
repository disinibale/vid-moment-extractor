# 🎮 Vid Moment Extractor

> A design blueprint for the project's README.

---

### **Canvas Layout: Main Banner**

Imagine a dark-themed banner at the top of the page.

* **Main Title (Large Font):**
    `Vid Moment Extractor`
* **Tagline (Smaller Font below Title):**
    `Automatically find and clip hype moments from your videos using AI transcription.`
* **Visual Graphic Idea:**
    A stylized video timeline where keywords like `"hahaha"`, `"anjing"`, and `"goblok"` are highlighted, with scissor icons (✂️) automatically snipping those segments.

---

### **How It Works: The Process Flow**

This section visually explains the script's pipeline from start to finish.

`▶️ Video File` ➔ `🧠 faster-whisper` ➔ `📝 Transcript` ➔ `🔍 Keyword Scan` ➔ `🚀 Parallel Jobs` ➔ `🎬 FFMPEG Clips`

* **`faster-whisper`**: Transcribes the video using your chosen model (`medium`, `small`, etc.).
* **`Keyword Scan`**: The script reads the transcript and finds timestamps for all your keywords.
* **`Parallel Jobs`**: Uses `ThreadPoolExecutor` to launch multiple `ffmpeg` processes at once.
* **`FFMPEG Clips`**: Encodes the final clips using hardware acceleration (`h264_nvenc`) for speed.

---

### **✨ Core Features (Icon Grid)**

Arrange these as five distinct visual blocks with icons.

| Icon | Feature                     | Description                                                                                       |
| :--: | --------------------------- | ------------------------------------------------------------------------------------------------- |
| `🚀` | **GPU-Accelerated Transcription** | Uses `faster-whisper` with CUDA (`float16`) for blazing-fast speech-to-text on NVIDIA GPUs. |
| `🎯` | **Custom Keyword Detection** | Define your own list of hype/funny words (e.g., "laugh", "gendut") to trigger a clip.         |
| `✂️` | **Automated Clipping** | Automatically exports video segments with configurable time buffers around each found keyword.    |
| `🧵` | **Parallel Exporting** | Leverages `ThreadPoolExecutor` to export multiple clips at the same time, saving you hours.     |
| `💻` | **Hardware Encoding** | Defaults to `h264_nvenc` for efficient video encoding, offloading work from the CPU.            |

---

### **🛠️ Configuration Panel (Visual Mockup)**

Imagine this section as a settings panel from an application.

> #### **`extract.py` Settings**
>
> **File Paths**
>
> `video_path`: [ `your_video.mkv` ]
>
> `clip_output_dir`: [ `clips/` ]
>
> ---
>
> **AI & Performance**
>
> `model_size`: [ `medium` ▼] (`small`, `large-v2`)
>
> `device`: [ `cuda` ▼] (`cpu`)
>
> `max_workers`: [ `6` ]
>
> ---
>
> **Clip Timing**
>
> `min_duration`: [ `60` ]s
>
> `buffer_before`: [ `1.5` ]s
>
> `buffer_after`: [ `3.0` ]s

---

### **🚀 Get Started in 3 Steps**

A clean, numbered guide for new users.

1.  **Install Dependencies**
    * Make sure `ffmpeg` is installed and in your system's PATH.
    * Install Python packages:
        ```bash
        pip install faster-whisper
        ```

2.  **Configure The Script**
    * Open `extract.py`.
    * Set your `video_path` to the correct file.
    * Customize your `keywords` list.

3.  **Run It!**
    * Execute the script from your terminal:
        ```bash
        python extract.py
        ```

---

### **📦 Output Preview**

A simple visual representation of what the user will get.

* 📄 **`transcript.txt`** (Full, timestamped transcript)
* 📁 **`clips/`**
    * `clip_1.mkv`
    * `clip_2.mkv`
    * `clip_3.mkv`
    * ...etc

---

### **💡 Pro-Tips & Troubleshooting**

> **💡 Not using an NVIDIA GPU?**
>
> The script defaults to `h264_nvenc`. If you get an FFMPEG error, open `extract.py` and find the `export_clip` function. Change `-c:v`, `"h264_nvenc"` to `-c:v`, `"libx264"` to use a more compatible software encoder.

> **😟 Getting CUDA or GPU errors?**
>
> Make sure to set `device = "cpu"` and `compute_type = "float32"` in the configuration section at the top of the script.
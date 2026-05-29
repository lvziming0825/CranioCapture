"""
CranioCapture

Frame extraction utility.

This script extracts evenly spaced frames from a smartphone video
using FFmpeg.

Example:
Extract ~50 frames from a 75-second video.

Author:
Richard LYU
"""

import os
import subprocess

ffmpeg_path = "your ffmpeg path"
video_path = "your raw video path"
output_dir = "output path"

os.makedirs(output_dir, exist_ok=True)

output_pattern = os.path.join(output_dir, "%05d.png")

# Number of frames to extract from the video
# In the proposed pipeline, approximately 50 frames are usually retained.
target_frames = 50

# Total video duration in seconds
video_duration_seconds = 75

fps = target_frames / video_duration_seconds

cmd = [
    ffmpeg_path,
    "-i", video_path,
    "-vf", f"fps={fps},scale=iw*0.5:ih*0.5",
    "-q:v", "1",
    output_pattern
]

subprocess.run(cmd, check=True)

print(f"Done: extracted frames at {fps:.4f} fps.")

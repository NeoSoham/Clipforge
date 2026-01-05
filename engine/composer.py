from pathlib import Path
import subprocess
from typing import List, Tuple


def trim_clips(
    video_path: Path,
    windows: List[Tuple[float, float]],
    out_dir: Path
) -> List[Path]:
    """
    Trim video clips using ffmpeg.
    windows: list of (start_sec, end_sec)
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    clip_paths = []

    for i, (start, end) in enumerate(windows, 1):
        duration = max(0.1, end - start)
        out_path = out_dir / f"clip_{i:03d}.mp4"

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start:.2f}",
            "-i", str(video_path),
            "-t", f"{duration:.2f}",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(out_path)
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        clip_paths.append(out_path)

    return clip_paths

def generate_thumbnail(video_path: Path, timestamp: float, out_path: Path):
    cmd=[
        "ffmpeg",
        "-y",
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_path)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
from pathlib import Path
import subprocess

def extract_frames(video_path: Path, out_dir: Path, fps: int = 10):
    out_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = out_dir / "frame_%05d.jpg"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        str(output_pattern)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    frames = sorted(out_dir.glob("frame_*.jpg"))
    return frames


def extract_audio(video_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "audio.wav"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        str(audio_path)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return audio_path

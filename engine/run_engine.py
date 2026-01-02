from pathlib import Path
from .preprocess import extract_frames, extract_audio
from .heuristics import (
    detect_motion_windows,
    select_top_windows,
    expand_windows,
    deduplicate_windows
)
from .composer import trim_clips, generate_thumbnail


def run_engine(video_path: Path):
    """
    Run the ClipForge engine on a video and return metadata.
    """

    processed = Path("data/processed") / video_path.stem
    frames_dir = processed / "frames"
    audio_dir = processed / "audio"
    clips_dir = Path("clips") / video_path.stem

    fps = 10.0

    # ----------------------------
    # 1️⃣ Preprocessing
    # ----------------------------
    extract_frames(video_path, frames_dir, fps=int(fps))
    extract_audio(video_path, audio_dir)

    # ----------------------------
    # 2️⃣ Motion detection
    # ----------------------------
    motion_windows = detect_motion_windows(frames_dir, fps)

    if not motion_windows:
        return []

    # ----------------------------
    # 3️⃣ Goal anchor selection
    # ----------------------------
    goal_candidates = select_top_windows(motion_windows, top_k=7)

    # drop score, keep (start, end)
    goal_windows = [(s, e) for s, e, _ in goal_candidates]

    # remove duplicates (same goal, replay, celebration)
    goal_windows = deduplicate_windows(goal_windows, min_gap_sec=20.0)

    # ----------------------------
    # 4️⃣ Expand to story clips
    # ----------------------------
    goal_windows = expand_windows(
        goal_windows,
        pre_sec=18.0,   # buildup
        post_sec=12.0   # celebration
    )

    # ----------------------------
    # 5️⃣ Trim clips
    # ----------------------------
    clips_dir.mkdir(parents=True, exist_ok=True)
    clip_paths = trim_clips(video_path, goal_windows, clips_dir)

    # ----------------------------
    # 6️⃣ Build metadata
    # ----------------------------
    metadata = []
    for i, ((start, end), path) in enumerate(zip(goal_windows, clip_paths), 1):
        clip_path=Path(path)
        thumbnail_path = clip_path.with_suffix(".jpg")

        generate_thumbnail(
            video_path=clip_path,
            timestamp=0,
            out_path=thumbnail_path,
        )
        metadata.append({
            "clip_id": f"goal_{i}",
            "type": "goal_story",
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 2),
            "path": str(clip_path),
            "thumbnail": str(thumbnail_path)
        })

    return metadata

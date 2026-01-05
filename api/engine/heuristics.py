from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np
import glob


def detect_motion_windows(
    frames_dir: Path,
    fps: float,
    threshold_factor: float = 2.5,
    window_sec: float = 2.0
) -> List[Tuple[float, float, float]]:
    """
    Detect visually interesting moments using motion intensity.
    Returns (start, end, score).
    """

    frame_files = sorted(glob.glob(str(frames_dir / "frame_*.jpg")))
    if len(frame_files) < 2:
        return []

    prev = cv2.imread(frame_files[0], cv2.IMREAD_GRAYSCALE)
    scores = []

    for f in frame_files[1:]:
        cur = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        diff = cv2.absdiff(cur, prev)
        scores.append(np.mean(diff))
        prev = cur

    scores = np.array(scores)
    mean = scores.mean()
    std = scores.std()
    threshold = mean + threshold_factor * std

    half = window_sec / 2.0
    windows = []

    for i in np.where(scores > threshold)[0]:
        t = (i + 1) / fps
        windows.append((
            max(0.0, t - half),
            t + half,
            scores[i]
        ))

    return windows


def select_top_windows(
    windows: List[Tuple[float, float, float]],
    top_k: int = 1
) -> List[Tuple[float, float, float]]:
    """
    Select strongest motion windows.
    """
    if not windows:
        return []
    return sorted(windows, key=lambda x: x[2], reverse=True)[:top_k]


def merge_windows(
    windows: List[Tuple[float, float]],
    gap_sec: float = 1.5
) -> List[Tuple[float, float]]:
    """
    Merge overlapping or nearby windows.
    """

    if not windows:
        return []

    windows = sorted(windows)
    merged = [windows[0]]

    for s, e in windows[1:]:
        ps, pe = merged[-1]
        if s - pe <= gap_sec:
            merged[-1] = (ps, max(pe, e))
        else:
            merged.append((s, e))

    return merged


def expand_windows(
    windows: List[Tuple[float, float]],
    pre_sec: float = 18.0,
    post_sec: float = 12.0
) -> List[Tuple[float, float]]:
    """
    Expand windows to include buildup and celebration.
    """
    return [
        (max(0.0, s - pre_sec), e + post_sec)
        for s, e in windows
    ]

def deduplicate_windows(
    windows: List[Tuple[float, float]],
    min_gap_sec: float = 20.0
) -> List[Tuple[float, float]]:
    if not windows:
        return []

    windows = sorted(windows)
    out = [windows[0]]

    for s, e in windows[1:]:
        ls, le = out[-1]
        if s - le >= min_gap_sec:
            out.append((s, e))
        else:
            out[-1] = (ls, max(le, e))

    return out

from pathlib import Path
from engine.run_engine import run_engine

meta = run_engine(Path("data/raw/fifa.mp4"))
print(meta)

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROGRESS_DIR = DATA_DIR / "progress"
STATE_FILE = Path(__file__).resolve().parent.parent / "state" / "settings.json"

def load_quiz(chapter: str, qtype: str):
    """Loads quiz data for a given chapter and type."""
    filename = DATA_DIR / f"quiz_{chapter}_{qtype}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_progress(chapter: str, qtype: str):
    """Loads progress for a given chapter and type."""
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROGRESS_DIR / f"learned_{chapter}_{qtype}.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_progress(chapter: str, qtype: str, progress: dict):
    """Saves progress for a given chapter and type."""
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROGRESS_DIR / f"learned_{chapter}_{qtype}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def reset_progress(chapter: str):
    """Resets the progress for a specific chapter."""
    save_progress(chapter, "single", {})
    save_progress(chapter, "multi", {})
    print(f"Progress for chapter '{chapter}' has been reset.")


def load_settings():
    """Loads app settings."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"questions_per_session": 10}, f)
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


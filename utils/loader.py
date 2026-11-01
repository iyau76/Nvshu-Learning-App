import json
import os
from pathlib import Path
import tempfile
import shutil
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
_storage_dir = None


def configure_storage(directory):
    """Use writable storage independent of bundled assets."""
    global _storage_dir
    _storage_dir = Path(directory)
    _storage_dir.mkdir(parents=True, exist_ok=True)


def storage_dir():
    if _storage_dir is not None:
        return _storage_dir
    override = os.environ.get("NVSHU_DATA_DIR")
    if override:
        configure_storage(override)
    else:
        from kivy.app import App
        app = App.get_running_app()
        if app is None:
            raise RuntimeError("Call configure_storage before using progress outside the app")
        configure_storage(app.user_data_dir)
    return _storage_dir


def read_json(path, default, backup_invalid=False):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, UnicodeDecodeError):
        if backup_invalid:
            shutil.copy2(path, path.with_name(path.name + f".invalid-{time.time_ns()}"))
        return default


def write_json(path, value):
    """Replace only after a complete write; retain the previous file on failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_quiz(chapter: str, qtype: str):
    # Invalid bundled content should fail visibly instead of masquerading as an empty chapter.
    path = DATA_DIR / f"quiz_{chapter}_{qtype}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def progress_path(chapter, qtype):
    return storage_dir() / "progress" / f"learned_{chapter}_{qtype}.json"


def load_progress(chapter: str, qtype: str):
    path = progress_path(chapter, qtype)
    source = path if path.exists() else DATA_DIR / "progress" / path.name
    value = read_json(source, {}, backup_invalid=source == path)
    if not isinstance(value, dict):
        value = {}
    # Released versions use array indices. Preserve their format and discard stale keys.
    valid_keys = {str(i) for i in range(len(load_quiz(chapter, qtype)))}
    result = {k: v for k, v in value.items()
              if k in valid_keys and type(v) is int and v >= 0}
    return result


def save_progress(chapter: str, qtype: str, progress: dict):
    write_json(progress_path(chapter, qtype), progress)


def reset_progress(chapter: str):
    for qtype in ("single", "multi"):
        save_progress(chapter, qtype, {})


def load_settings():
    path = storage_dir() / "settings.json"
    source = path if path.exists() else ROOT_DIR / "state" / "settings.json"
    value = read_json(source, {}, backup_invalid=source == path)
    if not isinstance(value, dict):
        value = {}
    count = value.get("questions_per_session", 10)
    if type(count) is not int or not 5 <= count <= 50:
        count = 10
    return {"questions_per_session": count}


def save_settings(settings):
    write_json(storage_dir() / "settings.json", settings)

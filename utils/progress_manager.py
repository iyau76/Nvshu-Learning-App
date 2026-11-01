from utils.loader import load_progress, reset_progress

CHAPTERS = ["basics", "history", "geography", "phonology", "heritage"]
Q_TYPES = ["single", "multi"]


def initialize_all_progress_files():
    for chapter in CHAPTERS:
        for qtype in Q_TYPES:
            load_progress(chapter, qtype)


def reset_chapter_progress(chapter_key):
    if chapter_key not in CHAPTERS:
        raise ValueError(f"Unknown chapter: {chapter_key}")
    reset_progress(chapter_key)

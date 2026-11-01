from utils.loader import load_progress
from utils.progress_manager import initialize_all_progress_files


def ensure_progress_file(chapter, qtype):
    load_progress(chapter, qtype)


def init_all_progress():
    initialize_all_progress_files()

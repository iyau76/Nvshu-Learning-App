import os
import json
from utils.loader import load_quiz

def ensure_progress_file(chapter, qtype):
    path = f"progress/learned_{chapter}_{qtype}.json"
    if not os.path.exists(path):
        quiz = load_quiz(chapter, qtype)
        progress = {str(i): 0 for i in range(len(quiz))}
        os.makedirs("progress", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)

def init_all_progress():
    for chapter in ["basics", "history", "geography", "phonology", "heritage"]:
        for qtype in ["single", "multi"]:
            ensure_progress_file(chapter, qtype)
import random
from utils.loader import load_quiz, load_progress, load_settings, save_progress

def get_question_indices(quiz, progress, mode='unlearned'):
    """
    Gets question indices based on the mode.
    'unlearned': questions answered correctly < 2 times.
    'learned': questions answered correctly >= 2 times.
    'all': all questions.
    """
    if mode == 'all':
        return list(range(len(quiz)))
    
    if mode == 'learned':
        return [i for i, _ in enumerate(quiz) if progress.get(str(i), 0) >= 2]
    
    # Default to 'unlearned'
    return [i for i, _ in enumerate(quiz) if progress.get(str(i), 0) < 2]

def draw_questions(chapter: str, mode: str = 'learn_new'):
    """
    Draws questions for a learning session.
    mode: 'learn_new' for unlearned questions, 'review_old' for learned questions.
    """
    settings = load_settings()
    total_to_draw = settings.get("questions_per_session", 10)

    quiz_single = load_quiz(chapter, "single")
    quiz_multi = load_quiz(chapter, "multi")

    prog_single = load_progress(chapter, "single")
    prog_multi = load_progress(chapter, "multi")

    # Determine the pool of questions to draw from based on the mode
    draw_mode = 'unlearned' if mode == 'learn_new' else 'learned'
    
    single_indices = get_question_indices(quiz_single, prog_single, draw_mode)
    multi_indices = get_question_indices(quiz_multi, prog_multi, draw_mode)

    # If no questions are available in the selected mode, return empty.
    if not single_indices and not multi_indices:
        return []

    result = []
    
    # Adjust total questions to draw if available are less than the setting
    total_available = len(single_indices) + len(multi_indices)
    total_to_draw = min(total_to_draw, total_available)

    while len(result) < total_to_draw:
        # Determine question type based on weight, fallback if one type is exhausted
        choice = random.choices(["single", "multi"], weights=[0.7, 0.3])[0]
        
        if choice == "single" and single_indices:
            idx = random.choice(single_indices)
            result.append(("single", idx, quiz_single[idx]))
            single_indices.remove(idx)
        elif choice == "multi" and multi_indices:
            idx = random.choice(multi_indices)
            result.append(("multi", idx, quiz_multi[idx]))
            multi_indices.remove(idx)
        elif single_indices: # Fallback to single if multi is chosen but unavailable
            idx = random.choice(single_indices)
            result.append(("single", idx, quiz_single[idx]))
            single_indices.remove(idx)
        elif multi_indices: # Fallback to multi if single is chosen but unavailable
            idx = random.choice(multi_indices)
            result.append(("multi", idx, quiz_multi[idx]))
            multi_indices.remove(idx)
        else:
            break # No more questions to draw
            
    return result

def update_progress(chapter: str, qtype: str, index: int, correct: bool, mode: str = 'learn_new'):
    """
    Updates the progress for a single question.
    In 'review_old' mode, progress is not updated.
    Returns the new consecutive correct count for that question.
    """
    if mode == 'review_old':
        key = str(index)
        progress = load_progress(chapter, qtype)
        return progress.get(key, 0)

    progress = load_progress(chapter, qtype)
    key = str(index)
    
    if correct:
        current_streak = progress.get(key, 0)
        new_streak = current_streak + 1
        progress[key] = new_streak
    else:
        progress[key] = 0
        new_streak = 0
        
    save_progress(chapter, qtype, progress)
    return new_streak

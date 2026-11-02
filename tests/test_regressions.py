import json
import os
from pathlib import Path
from unittest.mock import patch

os.environ['KIVY_NO_ARGS'] = '1'
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.base import EventLoop
import pytest
from utils import loader
from utils.quiz_logic import draw_questions, update_progress
from utils.progress_manager import reset_chapter_progress


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path):
    loader.configure_storage(tmp_path)


def test_corrupt_settings_and_progress_preserve_evidence(tmp_path):
    (tmp_path / 'settings.json').write_text('{broken', encoding='utf8')
    assert loader.load_settings()['questions_per_session'] == 10
    assert list(tmp_path.glob('settings.json.invalid-*'))
    path = loader.progress_path('basics', 'single')
    path.parent.mkdir()
    path.write_text('{broken', encoding='utf8')
    assert loader.load_progress('basics', 'single') == {}
    update_progress('basics', 'single', 0, True)
    assert list(path.parent.glob(path.name + '.invalid-*'))
    assert loader.load_progress('basics', 'single') == {'0': 1}


def test_atomic_failure_retains_previous_file(tmp_path):
    path = tmp_path / 'settings.json'
    loader.write_json(path, {'questions_per_session': 8})
    with patch('utils.loader.os.replace', side_effect=OSError('disk unavailable')):
        with pytest.raises(OSError):
            loader.write_json(path, {'questions_per_session': 20})
    assert json.loads(path.read_text()) == {'questions_per_session': 8}
    assert list(tmp_path.iterdir()) == [path]


def test_progress_cycle_review_reset_and_stale_keys():
    loader.save_progress('basics', 'single', {'0': 1, '999': 2, '1': 'bad', '2': -1})
    assert loader.load_progress('basics', 'single') == {'0': 1}
    assert update_progress('basics', 'single', 0, True) == 2
    assert update_progress('basics', 'single', 0, False, 'review_old') == 2
    assert update_progress('basics', 'single', 0, False) == 0
    reset_chapter_progress('basics')
    assert loader.load_progress('basics', 'single') == {}
    assert loader.load_progress('basics', 'multi') == {}


def test_draw_without_repeats_and_correct_pools():
    loader.save_settings({'questions_per_session': 50})
    questions = draw_questions('basics')
    assert len(questions) == 40
    assert len({(kind, index) for kind, index, _ in questions}) == 40
    loader.save_progress('basics', 'single', {'0': 2})
    assert [(kind, index) for kind, index, _ in draw_questions('basics', 'review_old')] == [('single', 0)]
    assert all((kind, index) != ('single', 0) for kind, index, _ in draw_questions('basics'))


def settle():
    import time
    deadline = time.monotonic() + 0.55
    while time.monotonic() < deadline:
        EventLoop.idle()


@pytest.fixture
def app(tmp_path):
    from main import NvshuApp
    os.environ['NVSHU_DATA_DIR'] = str(tmp_path)
    application = NvshuApp()
    application._run_prepare()
    Window.size = (390, 780)
    settle()
    yield application
    application.stop()
    os.environ.pop('NVSHU_DATA_DIR', None)


def test_real_widgets_multiselect_history_wrapping_and_review(app):
    screen = app.root.get_screen('learning')
    question = loader.load_quiz('history', 'multi')[2]
    with patch('screens.learning_screen.draw_questions', return_value=[('multi', 2, question)]):
        screen.chapter = 'history'
        app.root.current = 'learning'
        settle()
    # on_enter runs after the transition.
    screen.start_new_round = lambda *args: None
    if not screen.questions:
        pytest.fail('learning did not initialize')
    info = screen.session_data[0]
    button = info['option_widgets'][0]
    screen.toggle_selection(button)
    selected = button.text
    screen.render_current_question()
    settle()
    info = screen.session_data[0]
    restored = next(b for b in info['option_widgets'] if b.text == selected)
    assert tuple(restored.background_color) == pytest.approx((0.15, 0.42, 0.2, 1))
    assert info['user_selection'] == {selected}
    assert all(b.text_size[0] <= b.width for b in info['option_widgets'])
    assert any(b.height > 48 for b in info['option_widgets'])
    assert screen.ids.explanation_scroll.height == 0
    screen.check_answer(set())
    assert not screen.session_data[0]['history'][0]['is_correct']
    settle()
    Path('artifacts/screenshots').mkdir(parents=True, exist_ok=True)
    screen.export_to_png('artifacts/screenshots/answer.png')
    assert all(tuple(b.disabled_color) == (1, 1, 1, 1) for b in screen.session_data[0]['option_widgets'])
    screen.start_new_pass()
    screen.check_answer(set(screen.session_data[0]['correct_answers']))
    screen.start_new_pass()
    screen.check_answer(set(screen.session_data[0]['correct_answers']))
    assert len(screen.session_data[0]['history']) == 3
    assert loader.load_progress('history', 'multi')['2'] == 2
    review = app.root.get_screen('review')
    review.questions = screen.questions
    review.session_data = screen.session_data
    review.learning_screen = screen
    app.root.current = 'review'
    settle()
    review.generate_report()
    settle()
    assert any('第 1 次错答' in label.text for label in review.ids.review_container.children)
    output = Path('artifacts/screenshots')
    output.mkdir(parents=True, exist_ok=True)
    review.export_to_png(str(output / 'review.png'))
    # Resize without losing wrapping.
    Window.size = (360, 720)
    settle()
    assert all(label.text_size[0] <= label.width for label in review.ids.review_container.children)


def test_real_settings_layout_save_back_pause(app):
    app.root.current = 'settings'
    settle()
    settings = app.root.get_screen('settings')
    settings.ids.questions_input.text = '17'
    settings.save_settings()
    assert loader.load_settings()['questions_per_session'] == 17
    from kivy.uix.modalview import ModalView
    for widget in list(Window.children):
        if isinstance(widget, ModalView):
            widget.dismiss(animation=False)
    settle()
    box = settings.ids.questions_input.parent
    assert box.height >= 96 + 20 + 18
    output = Path('artifacts/screenshots')
    output.mkdir(parents=True, exist_ok=True)
    settings.export_to_png(str(output / 'settings.png'))
    assert app.handle_back(Window, 27)
    assert app.root.current == 'menu'
    assert app.on_pause() is True


def test_legacy_read_does_not_require_write_access():
    with patch('utils.loader.write_json', side_effect=OSError('read-only')):
        assert isinstance(loader.load_progress('basics', 'single'), dict)
        assert len(draw_questions('basics')) > 0


def test_failed_answer_can_be_retried(app):
    screen = app.root.get_screen('learning')
    question = loader.load_quiz('basics', 'single')[0]
    with patch('screens.learning_screen.draw_questions', return_value=[('single', 0, question)]):
        screen.chapter = 'basics'
        app.root.current = 'learning'
        settle()
    selected = screen.session_data[0]['correct_answers'][0]
    with patch('screens.learning_screen.update_progress', side_effect=OSError('read-only')):
        screen.check_answer(selected)
    assert not screen.session_data[0].get('answered')
    assert not screen.session_data[0]['history']
    from kivy.uix.modalview import ModalView
    for widget in list(Window.children):
        if isinstance(widget, ModalView):
            widget.dismiss(animation=False)
    screen.check_answer(selected)
    assert screen.session_data[0]['answered']
    assert loader.load_progress('basics', 'single')['0'] == 1


def test_original_quiz_and_assets_are_unchanged():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'tests/content.sha256.json').read_text(encoding='utf8'))
    for relative, expected in manifest.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative

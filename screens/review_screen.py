from kivy.uix.label import Label
from kivy.utils import escape_markup
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.logger import Logger
class ReviewScreen(Screen):
    """
    A screen that displays a text-based report of the last session.
    """
    session_data = ListProperty([])
    review_text = StringProperty("")
    learning_screen = ObjectProperty(None, allownone=True)
    questions = ListProperty([])
    def on_pre_enter(self):
        Clock.schedule_once(self.delayed_generate_report, 0.1)

    def delayed_generate_report(self, dt):
        try:
            self.generate_report()
        except Exception as e:
            Logger.error(f"🧨 generate_report() 调用失败: {e}")


    def generate_report(self):
        self.ids.review_scroll.scroll_y = 1

        container = self.ids.review_container
        container.clear_widgets()

        for index, q_data in enumerate(self.questions):
            session_info = self.session_data[index]
            q_type, _, question = q_data

            blocks = []

            blocks.append(f"[b]第 {index + 1} 题 ({'单选' if q_type == 'single' else '多选'})[/b]")
            blocks.append(escape_markup(question['question']))

            options = session_info.get('options_shuffled', [])
            correct_answers = session_info.get('correct_answers', [])
            user_selection = session_info.get('user_selection', set())

            for i, opt_text in enumerate(options):
                option_char = chr(ord('A') + i)
                display_line = f"{option_char}. {escape_markup(opt_text)}"

                if opt_text in correct_answers:
                    display_line += " [color=33FF33](正确答案)[/color]"
                if opt_text in user_selection and opt_text not in correct_answers:
                    display_line += " [color=FF5733](我的错误选择)[/color]"

                blocks.append(display_line)

            if self.learning_screen:
                if 'is_correct' in session_info:
                    is_correct = session_info.get('is_correct', False)
                    result_str = "[color=33FF33]回答正确[/color]" if is_correct else "[color=FF5733]回答错误[/color]"
                    blocks.append(f"[b]作答结果：[/b] {result_str}")
                else:
                    blocks.append("[b]作答结果：[/b] 本题未作答。")

            for attempt, record in enumerate(session_info.get('history', []), 1):
                if not record['is_correct']:
                    selected = '；'.join(record['user_selection']) or '未选择'
                    answers = '；'.join(record['correct_answers'])
                    blocks.append(f"[b]第 {attempt} 次错答：[/b] {escape_markup(selected)}")
                    blocks.append(f"[b]当次正确答案：[/b] {escape_markup(answers)}")
            blocks.append(f"[b]解析：[/b] {escape_markup(question.get('explanation', '暂无解析。'))}")
            blocks.append("-" * 40)

            for line in blocks:
                lbl = Label(
                    text=line,
                    markup=True,
                    font_name="NvshuFont",
                    font_size="16sp",
                    size_hint_y=None,
                    text_size=(self.width - 40, None),
                    color=(1, 1, 1, 1),
                )
                lbl.bind(width=lambda widget, width: setattr(widget, 'text_size', (max(dp(1), width - dp(20)), None)))
                lbl.bind(texture_size=lambda widget, size: setattr(widget, 'height', size[1] + dp(10)))
                lbl.texture_update()
                lbl.height = lbl.texture_size[1] + 10
                container.add_widget(lbl)
    def back_to_menu(self):
        """
        Clears session data and returns to the main menu.
        """
        self.session_data = []
        self.questions = []
        self.learning_screen = None
        self.manager.current = 'menu'

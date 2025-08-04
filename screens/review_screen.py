from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, ObjectProperty

class ReviewScreen(Screen):
    """
    A screen that displays a text-based report of the last session.
    """
    session_data = ListProperty([])
    learning_screen = ObjectProperty(None, allownone=True)
    questions = ListProperty([])

    def on_enter(self, *args):
        """
        Generates and displays the text report.
        """
        self.generate_report()

    def generate_report(self):
        """
        Generates a full text report for the session.
        """
        report_text = ""
        
        for index, q_data in enumerate(self.questions):
            session_info = self.session_data[index]
            q_type, _, question = q_data
            
            report_text += f"[b]第 {index + 1} 题 ({'单选' if q_type == 'single' else '多选'})[/b]\n"
            report_text += f"{question['question']}\n\n"

            options = session_info.get('options_shuffled', [])
            correct_answers = session_info.get('correct_answers', [])
            user_selection = session_info.get('user_selection', set())
            
            for i, opt_text in enumerate(options):
                option_char = chr(ord('A') + i)
                display_line = f"{option_char}. {opt_text}"
                
                if opt_text in correct_answers:
                    display_line += " [color=33FF33](正确答案)[/color]"
                
                if opt_text in user_selection and opt_text not in correct_answers:
                     display_line += " [color=FF5733](我的错误选择)[/color]"
                
                report_text += display_line + "\n"
            
            report_text += "\n"

            if self.learning_screen.mode == 'learn_new':
                total_attempts = session_info.get('attempts', 0)
                if total_attempts > 0:
                    report_text += f""
                else:
                    report_text += f""

            else: # review_old
                if 'is_correct' in session_info:
                    is_correct = session_info.get('is_correct', False)
                    result_str = "[color=33FF33]回答正确[/color]" if is_correct else "[color=FF5733]回答错误[/color]"
                    report_text += f"[b]作答结果：[/b] {result_str}\n"
                else:
                    report_text += f"[b]作答结果：[/b] 本题未作答。\n"


            report_text += f"[b]解析：[/b] {question.get('explanation', '暂无解析。')}\n"
            report_text += "-"*30 + "\n\n"

        self.ids.review_content_label.text = report_text
        self.ids.review_content_label.font_size = '16sp'


    def back_to_menu(self):
        """
        Clears session data and returns to the main menu.
        """
        self.session_data = []
        self.questions = []
        self.learning_screen = None
        self.manager.current = 'menu'

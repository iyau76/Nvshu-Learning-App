import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty, BooleanProperty

from utils.quiz_logic import draw_questions, update_progress
from utils.loader import load_progress

class LearningScreen(Screen):
    chapter = StringProperty("")
    mode = StringProperty("learn_new")
    
    questions = ListProperty([])
    session_data = ListProperty([])
    pass_indices = ListProperty([]) 
    current_pass_pos = NumericProperty(0) 
    
    def on_enter(self, *args):
        self.start_new_round()

    def start_new_round(self, *args):
        """Initializes a learning round with a fixed set of 10 questions."""
        self.questions = draw_questions(self.chapter, self.mode)
        if not self.questions:
            self.show_no_questions_popup()
            return

        self.session_data = [{} for _ in self.questions]
        self.start_new_pass()

    def start_new_pass(self):
        """Starts a new loop (pass) through questions not yet learned."""
        if self.mode == 'learn_new':
            self.pass_indices = [
                i for i, (qtype, qidx, _) in enumerate(self.questions)
                if load_progress(self.chapter, qtype).get(str(qidx), 0) < 2
            ]
            if not self.pass_indices:
                self.show_end_of_round_popup()
                return
        else: # review_old mode
            self.pass_indices = list(range(len(self.questions)))

        for i in self.pass_indices:
            self.session_data[i] = {}
        
        self.current_pass_pos = 0
        self.render_current_question()

    def render_current_question(self):
        """Renders the question at the current position in the current pass."""
        if not self.pass_indices: return
        current_q_index = self.pass_indices[self.current_pass_pos]
        
        self.ids.content_area.clear_widgets()
        self.ids.explanation_scroll.height = 0
        self.ids.explanation_scroll.opacity = 0
        self.update_ui_state()

        q_data = self.questions[current_q_index]
        session_info = self.session_data[current_q_index]
        qtype, _, question = q_data

        q_text = f"[{'单选' if qtype == 'single' else '多选'}]\n\n{question['question']}"
        q_label = Label(text=q_text, font_size="22sp", size_hint_y=None, text_size=(self.width*0.85, None), halign='left')
        q_label.bind(texture_size=lambda i, v: setattr(i, 'height', v[1]))
        
        q_scroll = ScrollView(size_hint_y=0.4, do_scroll_x=False); q_scroll.add_widget(q_label)
        self.ids.content_area.add_widget(q_scroll)

        options_box = self.build_options(q_data, session_info)
        opt_scroll = ScrollView(size_hint_y=0.6, do_scroll_x=False); opt_scroll.add_widget(options_box)
        self.ids.content_area.add_widget(opt_scroll)

        if session_info.get('answered'):
            self.show_feedback(session_info)

    def build_options(self, q_data, session_info):
        """Builds the answer option widgets for the current question."""
        qtype, _, question = q_data
        container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        if 'options_shuffled' not in session_info:
            if qtype == "single":
                correct = random.choice(question["correct_answers"])
                session_info['correct_answers'] = [correct]
                wrongs = random.sample(question["wrong_options"], min(3, len(question["wrong_options"])))
                options = wrongs + [correct]
            else:
                corrects = question["correct_answers"]
                num_corrects = random.randint(2, min(3, len(corrects)))
                corrects_sample = random.sample(corrects, num_corrects)
                session_info['correct_answers'] = corrects_sample
                num_wrongs = max(1, 5 - len(corrects_sample))
                wrongs_sample = random.sample(question["wrong_options"], min(len(question["wrong_options"]), num_wrongs))
                options = corrects_sample + wrongs_sample
            random.shuffle(options)
            session_info['options_shuffled'] = options
        
        options = session_info.get('options_shuffled', [])
        session_info['option_widgets'] = []
        for opt_text in options:
            btn = Button(text=opt_text, font_size="18sp", size_hint_y=None, height="48dp")
            session_info['option_widgets'].append(btn)
            if qtype == 'single':
                btn.bind(on_release=lambda instance, s=opt_text: self.check_answer(s))
            else: # multi
                btn.background_color = (0.5, 0.5, 0.5, 1)
                btn.bind(on_release=self.toggle_selection)
            container.add_widget(btn)

        if qtype == 'multi':
            submit_btn = Button(text="提交选择", size_hint_y=None, height="48dp", font_size='24sp')
            submit_btn.bind(on_release=lambda b: self.check_answer(session_info.get('user_selection', set())))
            container.add_widget(submit_btn)
            session_info['submit_button'] = submit_btn
        return container

    def toggle_selection(self, btn):
        """Handles selection for multiple-choice questions."""
        current_q_index = self.pass_indices[self.current_pass_pos]
        session_info = self.session_data[current_q_index]
        selection_set = session_info.setdefault('user_selection', set())
        if btn.text in selection_set:
            selection_set.remove(btn.text)
            btn.background_color = (0.5, 0.5, 0.5, 1)
        else:
            selection_set.add(btn.text)
            btn.background_color = (0.3, 0.7, 0.3, 1)

    def check_answer(self, user_selection):
        """Checks the user's answer, updates progress, and shows feedback."""
        current_q_index = self.pass_indices[self.current_pass_pos]
        session_info = self.session_data[current_q_index]
        if session_info.get('answered'): return

        qtype, qidx, _ = self.questions[current_q_index]
        correct_answers = session_info['correct_answers']
        
        is_correct = (set(user_selection) == set(correct_answers)) if qtype == 'multi' else (user_selection in correct_answers)
        
        session_info['answered'] = True
        session_info['is_correct'] = is_correct
        session_info['user_selection'] = {user_selection} if qtype == 'single' else user_selection
        session_info['attempts'] = session_info.get('attempts', 0) + 1

        update_progress(self.chapter, qtype, qidx, is_correct, self.mode)
        self.show_feedback(session_info)
        self.update_ui_state()

    def show_feedback(self, session_info):
        """Displays visual feedback (colors, explanation) after an answer."""
        for btn in session_info.get('option_widgets', []): btn.disabled = True
        if 'submit_button' in session_info: session_info['submit_button'].disabled = True
        
        user_selection = session_info.get('user_selection', set())
        correct_answers = session_info.get('correct_answers', [])
        for btn in session_info.get('option_widgets', []):
            if btn.text in user_selection:
                btn.background_color = (0.2, 0.8, 0.2, 1) if btn.text in correct_answers else (0.9, 0.3, 0.3, 1)
            elif btn.text in correct_answers:
                btn.background_color = (0.2, 0.8, 0.2, 1)
            else:
                btn.background_color = (0.2, 0.2, 0.2, 1)

        is_correct = session_info.get('is_correct', False)
        result_text = "[color=33FF33]回答正确！[/color]\n\n" if is_correct else "[color=FF5733]回答错误。[/color]\n\n"
        explanation = self.questions[self.pass_indices[self.current_pass_pos]][2].get("explanation", "暂无解析。")
        self.ids.explanation_label.text = result_text + explanation
        self.ids.explanation_scroll.height = self.height * 0.3
        self.ids.explanation_scroll.opacity = 1
        self.ids.explanation_label.font_size = '18sp'

    def next_question(self, *args):
        """Moves to the next question in the pass, or starts a new pass."""
        if self.current_pass_pos < len(self.pass_indices) - 1:
            self.current_pass_pos += 1
            self.render_current_question()
        else:
            if self.mode == 'review_old':
                self.show_end_of_round_popup()
            else:
                self.start_new_pass()

    def prev_question(self, *args):
        """Moves to the previous question in the current pass."""
        if self.current_pass_pos > 0:
            self.current_pass_pos -= 1
            self.render_current_question()
    
    def update_ui_state(self):
        """Updates UI elements like labels and button states."""
        if not self.pass_indices: return
        
        if self.mode == 'learn_new':
            learned_count = sum(1 for q_type, q_idx, _ in self.questions if load_progress(self.chapter, q_type).get(str(q_idx), 0) >= 2)
            self.ids.learned_label.text = f"本轮学会: {learned_count}/{len(self.questions)}"
            self.ids.learned_label.font_size = '18sp'
        else:
            self.ids.learned_label.text = f"复习进度: {self.current_pass_pos + 1}/{len(self.pass_indices)}"
            self.ids.learned_label.font_size = '18sp'


        self.ids.prev_button.disabled = self.current_pass_pos <= 0
        current_q_index = self.pass_indices[self.current_pass_pos]
        has_answered = self.session_data[current_q_index].get('answered', False)
        self.ids.next_button.disabled = not has_answered

    def show_end_of_round_popup(self):
        """Shows the end-of-round summary popup."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=20)
        message = '本轮复习已完成！' if self.mode == 'review_old' else '恭喜！本轮题目已全部学会！'
        content.add_widget(Label(text=message, font_name="NvshuFont", font_size='24sp'))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height='50dp')
        popup = Popup(title='恭喜    𛈌𛆻', title_font='NvshuFont', content=content, size_hint=(0.9, 0.5), auto_dismiss=False)
        
        review_btn = Button(text='复盘\n𛋷𛋅', font_size='20sp')
        review_btn.bind(on_release=lambda x: self.go_to_review(popup))
        btn_layout.add_widget(review_btn)

        if self.mode == 'learn_new':
            continue_btn = Button(text='再学一组\n𛇥𛉬𛆼𛊽', font_size='20sp')
            continue_btn.bind(on_release=lambda x: popup.dismiss(), on_press=self.start_new_round)
            btn_layout.add_widget(continue_btn)

        menu_btn = Button(text='主菜单\n𛋱𛈠𛈁', font_size='20sp')
        menu_btn.bind(on_release=lambda x: self.go_to_menu(popup))
        btn_layout.add_widget(menu_btn)
        
        content.add_widget(btn_layout)
        popup.open()

    def go_to_menu(self, popup):
        popup.dismiss()
        self.manager.current = 'menu'

    def go_to_review(self, popup):
        popup.dismiss()
        review_screen = self.manager.get_screen('review')
        review_screen.session_data = self.session_data
        review_screen.questions = self.questions
        review_screen.learning_screen = self
        self.manager.current = 'review'

    def show_no_questions_popup(self):
        """Shows a popup when no questions are available to draw."""
        message = '太棒了！\n本章节已没有新题目可学！' if self.mode == 'learn_new' else '本章节还没有已学会的题目，\n快去“学习新知”吧！'
        content = BoxLayout(orientation='vertical', padding=10, spacing=20)
        content.add_widget(Label(text=message, font_name="NvshuFont", font_size='24sp', halign='center'))
        menu_btn = Button(text='返回章节选择', size_hint_y=None, height='48dp', font_size='20sp')
        popup = Popup(title='提示    𛊹𛆹', title_font='NvshuFont', content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        
        # 关键修复：使用一个辅助函数来正确处理关闭弹窗和屏幕跳转的顺序。
        def close_and_go_back(instance):
            popup.dismiss()
            self.manager.current = 'chapter'

        # 错误写法：menu_btn.bind(on_release=popup.dismiss())
        # 正确写法：将函数本身（callable）传递给 on_release
        menu_btn.bind(on_release=close_and_go_back)
        content.add_widget(menu_btn)
        popup.open()

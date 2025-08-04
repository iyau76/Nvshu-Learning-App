from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from utils.loader import load_quiz, load_progress
# 关键：从我们新的 progress_manager 导入重置函数
from utils.progress_manager import reset_chapter_progress

class ChapterScreen(Screen):
    chapter_map = {
            "basics": "女书基本知识    𛆁𛈬𛋔𛇅𛇟𛊗", "history": "历史    𛉭𛆹", "geography": "地理    𛋇𛉄",
            "phonology": "字音字形    𛈤𛆱𛈤𛊁", "heritage": "非遗保护与田野调查    𛆌𛆱𛈆𛋙𛉟𛋊𛇩𛉑𛉗"
        }
    def on_pre_enter(self, *args):
        """进入屏幕前，刷新章节列表和进度。"""
        self.populate_chapters()

    def populate_chapters(self):
        """清除并重新填充章节列表及其当前进度。"""
        self.ids.chapter_box.clear_widgets()

        for key, title in self.chapter_map.items():
            single_total = len(load_quiz(key, "single"))
            multi_total = len(load_quiz(key, "multi"))
            total_questions = single_total + multi_total

            if total_questions == 0: continue

            single_prog = load_progress(key, "single")
            multi_prog = load_progress(key, "multi")
            
            single_learned = sum(1 for v in single_prog.values() if v >= 2)
            multi_learned = sum(1 for v in multi_prog.values() if v >= 2)
            total_learned = single_learned + multi_learned
            progress_rate = (total_learned / total_questions) * 100

            progress_text = f"{title}\n进度: {progress_rate:.2f}%    𛉑𛋥：{total_learned}/{total_questions}"
            btn = Button(text=progress_text, font_size="20sp", font_name="NvshuFont", size_hint_y=None, height="70dp", halign='center')
            btn.bind(on_release=lambda b, k=key, t=title, p=(total_learned/total_questions if total_questions > 0 else 0): self.show_chapter_options(k, t, p))
            self.ids.chapter_box.add_widget(btn)
            

    def show_chapter_options(self, chapter_key, chapter_title, progress_ratio):
        """根据章节进度，显示不同的学习选项弹窗。"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup = Popup(title=chapter_title, content=content, size_hint=(0.9, 0.5), auto_dismiss=True, title_font='NvshuFont')

        if progress_ratio >= 1.0:
            content.add_widget(Label(text='恭喜！本章已全部学会！', font_name="NvshuFont", font_size='24sp'))
            
            review_btn = Button(text='复习旧闻\n𛋷𛆓𛆝𛋁', font_name="NvshuFont", font_size='20sp')
            # 绑定事件：先关闭当前弹窗，然后开始学习
            review_btn.bind(on_release=lambda x: (popup.dismiss(), self.start_learning(chapter_key, 'review_old')))
            content.add_widget(review_btn)

            reset_btn = Button(text='重置学习进度\n𛊻𛋔𛉬𛆓𛉑𛋥', font_name="NvshuFont", font_size='20sp')
            # 关键：绑定到新的、统一的确认流程
            reset_btn.bind(on_release=lambda x: (popup.dismiss(), self.confirm_reset(chapter_key)))
            content.add_widget(reset_btn)

        else:
            learn_btn = Button(text='学习新知\n𛉬𛆓𛊛𛇟', font_name="NvshuFont", font_size=36)
            learn_btn.bind(on_release=lambda x: (popup.dismiss(), self.start_learning(chapter_key, 'learn_new')))
            content.add_widget(learn_btn)
            
            review_btn = Button(text='复习旧闻\n𛋷𛆓𛆝𛋁', font_name="NvshuFont", font_size=36)
            review_btn.bind(on_release=lambda x: (popup.dismiss(), self.start_learning(chapter_key, 'review_old')))
            content.add_widget(review_btn)

        popup.open()
        
    def confirm_reset(self, chapter_key):
        """
        (与settings_screen.py同步)
        显示最终确认弹窗，防止误操作。
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"您确定要重置\n'{self.get_chapter_display_name(chapter_key)}'\n的所有学习进度吗？\n此操作不可撤销！", halign='center', font_size='20sp'))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height='48dp')
        yes_btn = Button(text='确定重置\n𛆄𛉽𛊻𛋔', font_size='20sp')
        no_btn = Button(text='取消\n𛉛𛈨', font_size='20sp')
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        confirm_popup = Popup(title='请再次确认    𛉁𛇥𛇠𛆄𛅺', title_font='NvshuFont', content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        
        yes_btn.bind(on_release=lambda x: self.do_reset(chapter_key, confirm_popup))
        no_btn.bind(on_release=confirm_popup.dismiss)
        
        confirm_popup.open()
        
    def do_reset(self, chapter_key, popup_to_dismiss):
        """
        (与settings_screen.py同步)
        执行重置，显示反馈，并刷新本页面。
        """
        popup_to_dismiss.dismiss()
        reset_chapter_progress(chapter_key)
        self.show_feedback_popup(title="操作完成    𛋴𛊅𛆧𛈒", message=f"'{self.get_chapter_display_name(chapter_key)}' 的进度已重置。")
        # 核心：重置后，刷新章节列表以立即看到变化
        self.populate_chapters()

    def show_feedback_popup(self, title, message):
        """
        (与settings_screen.py同步)
        通用的反馈弹窗。
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, halign='center'))
        ok_btn = Button(text='好的', size_hint_y=None, height='48dp')
        content.add_widget(ok_btn)
        popup = Popup(title=title, title_font='NvshuFont', content=content, size_hint=(0.7, 0.4))
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def get_chapter_display_name(self, key):
        """
        (与settings_screen.py同步)
        辅助函数，根据key获取章节的中文名。
        """

        return self.chapter_map.get(key, key)

    def start_learning(self, chapter_key, mode):
        """切换到学习屏幕，并传递章节和模式。"""
        learning_screen = self.manager.get_screen("learning")
        learning_screen.chapter = chapter_key
        learning_screen.mode = mode
        self.manager.current = "learning"

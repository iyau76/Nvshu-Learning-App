import json

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView # 关键：导入 ScrollView
from kivy.properties import StringProperty

from utils.loader import load_settings, STATE_FILE
from utils.progress_manager import reset_chapter_progress, CHAPTERS

from screens.chapter_screen import ChapterScreen

class SettingsScreen(Screen):
    questions_per_session_text = StringProperty("")

    def on_pre_enter(self, *args):
        """进入屏幕前，加载当前设置并显示。"""
        self.load_current_settings()

    def load_current_settings(self):
        """加载每轮题量设置并更新UI。"""
        settings = load_settings()
        self.questions_per_session_text = str(settings.get("questions_per_session", 10))

    def save_settings(self):
        """保存用户输入的题量设置。"""
        try:
            num = int(self.ids.questions_input.text)
            if 5 <= num <= 50: # 合理范围检查
                settings = load_settings()
                settings["questions_per_session"] = num
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
                self.show_feedback_popup("成功    𛈒𛇕", "设置已保存！")
            else:
                self.show_feedback_popup("错误    𛋞𛊃", "请输入一个 5 到 50 之间的整数。")
        except ValueError:
            self.show_feedback_popup("错误    𛋞𛊃", "请输入有效的数字！")
        except Exception as e:
            self.show_feedback_popup("保存失败    𛉎𛊶𛊼𛇣", f"发生未知错误：\n{e}")


    def show_reset_options(self):
        """显示一个包含所有章节的弹窗，让用户选择要重置哪一章。"""
        # 弹窗的主布局
        popup_content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_content_layout.add_widget(Label(text="请选择要重置进度的章节：", size_hint_y=None, height='30dp'))

        # 关键修复：创建一个 BoxLayout 来容纳所有按钮
        button_grid = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        button_grid.bind(minimum_height=button_grid.setter('height'))

        # 关键修复：创建一个 ScrollView，并将按钮列表（button_grid）放入其中
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(button_grid)

        # 将可以滚动的 ScrollView 添加到弹窗主布局中
        popup_content_layout.add_widget(scroll_view)

        # 章节名称映射
        chapter_map = ChapterScreen.chapter_map
        print(chapter_map)
        # 动态生成所有章节的重置按钮，并添加到 button_grid 中
        for chapter_key in CHAPTERS:
            btn = Button(text=f"重置：{chapter_map.get(chapter_key, chapter_key)}", size_hint_y=None, height='48dp')
            btn.bind(on_release=lambda instance, k=chapter_key: self.confirm_reset(k))
            button_grid.add_widget(btn)

        # 创建并打开弹窗
        self.reset_popup = Popup(
            title="重置学习进度    𛊻𛋔𛉬𛆓𛉑𛋥",
            title_font='NvshuFont',
            content=popup_content_layout,
            size_hint=(0.9, 0.8)
        )
        self.reset_popup.open()

    def confirm_reset(self, chapter_key):
        """显示最终确认弹窗，防止误操作。"""
        if hasattr(self, 'reset_popup'):
            self.reset_popup.dismiss()

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"您确定要重置\n'{self.get_chapter_display_name(chapter_key)}'\n的所有学习进度吗？\n此操作不可撤销！", font_size='20sp', halign='center'))
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height='48dp')
        yes_btn = Button(text='确定重置\n𛆄𛉽𛊻𛋔', font_size='20sp')
        no_btn = Button(text='取消\n𛉛𛈨', font_size='20sp')
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        confirm_popup = Popup(title='请再次确认    𛉁𛇥𛇠𛆄𛅺',title_font='NvshuFont', content=content, size_hint=(0.8, 0.5), auto_dismiss=False)
        
        yes_btn.bind(on_release=lambda x: self.do_reset(chapter_key, confirm_popup))
        no_btn.bind(on_release=confirm_popup.dismiss)
        
        confirm_popup.open()

    def do_reset(self, chapter_key, popup_to_dismiss):
        """执行重置操作并关闭弹窗。"""
        popup_to_dismiss.dismiss()
        reset_chapter_progress(chapter_key)
        self.show_feedback_popup("操作完成    𛋴𛊅𛆧𛈒", f"'{self.get_chapter_display_name(chapter_key)}' 的进度已重置。")

    def show_feedback_popup(self, title, message):
        """通用的反馈弹窗。"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, halign='center', font_size='20sp'))
        ok_btn = Button(text='好的', size_hint_y=None, height='48dp', font_size='20sp')
        content.add_widget(ok_btn)
        popup = Popup(title=title, title_font='NvshuFont', content=content, size_hint=(0.7, 0.4))
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def get_chapter_display_name(self, key):
        """辅助函数，根据key获取章节的中文名。"""
        chapter_map = ChapterScreen.chapter_map
        return chapter_map.get(key, key)

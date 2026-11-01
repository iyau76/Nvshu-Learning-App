from pathlib import Path
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.resources import resource_add_path

from screens.menu_screen import MenuScreen
from screens.chapter_screen import ChapterScreen
from screens.learning_screen import LearningScreen
from screens.testing_screen import TestingScreen
from screens.settings_screen import SettingsScreen
from screens.review_screen import ReviewScreen
from utils.loader import configure_storage

ROOT_DIR = Path(__file__).resolve().parent
resource_add_path(str(ROOT_DIR))
LabelBase.register(name="NvshuFont", fn_regular=str(ROOT_DIR / "assets/fonts/NyushuFirmiaItal-1.003.ttf"))
Builder.load_file(str(ROOT_DIR / "app.kv"))


class NvshuApp(App):
    def build(self):
        configure_storage(os.environ.get("NVSHU_DATA_DIR", self.user_data_dir))
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ChapterScreen(name='chapter'))
        sm.add_widget(LearningScreen(name='learning'))
        sm.add_widget(TestingScreen(name='testing'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ReviewScreen(name='review'))
        Window.bind(on_keyboard=self.handle_back)
        return sm

    def handle_back(self, window, key, *args):
        if key != 27 or not self.root:
            return False
        if any(isinstance(widget, ModalView) for widget in Window.children):
            return False
        if self.root.current == 'learning':
            self.root.current = 'chapter'
        elif self.root.current == 'review':
            self.root.get_screen('review').back_to_menu()
        elif self.root.current != 'menu':
            self.root.current = 'menu'
        else:
            return False
        return True

    def on_pause(self):
        return True

    def on_stop(self):
        Window.unbind(on_keyboard=self.handle_back)


if __name__ == '__main__':
    NvshuApp().run()

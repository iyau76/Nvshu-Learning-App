from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import ListProperty

from screens.menu_screen import MenuScreen
from screens.chapter_screen import ChapterScreen
from screens.learning_screen import LearningScreen
from screens.testing_screen import TestingScreen
from screens.settings_screen import SettingsScreen
from screens.review_screen import ReviewScreen

# =============================================================
# Custom ScreenManager with History Tracking
# =============================================================
class HistoryScreenManager(ScreenManager):
    """
    A custom ScreenManager that keeps track of the screen history.
    """
    history = ListProperty()

    def on_current(self, instance, value):
        """
        Called whenever the 'current' screen changes. We use this to
        update our history list.
        """
        # The 'current' property is the name of the screen (a string).
        # We find the actual screen widget from the name.
        screen_widget = self.get_screen(value)
        
        # Avoid adding the same screen twice in a row
        if not self.history or self.history[-1] != screen_widget:
            self.history.append(screen_widget)
        super(HistoryScreenManager, self).on_current(instance, value)

    def get_previous_screen_name(self):
        """
        Returns the name of the previously visited screen.
        """
        if len(self.history) > 1:
            return self.history[-2].name
        return None

# =============================================================

Builder.load_file("app.kv")

# Register the custom font
LabelBase.register(name="NvshuFont", fn_regular="assets/fonts/NyushuFirmiaItal-1.003.ttf")

class NvshuApp(App):
    def build(self):
        # Use our custom HistoryScreenManager instead of the default one
        sm = HistoryScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ChapterScreen(name='chapter'))
        sm.add_widget(LearningScreen(name='learning'))
        sm.add_widget(TestingScreen(name='testing'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ReviewScreen(name='review'))
        return sm

if __name__ == '__main__':
    NvshuApp().run()

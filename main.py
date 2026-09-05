import os
import re
import threading

from gtts import gTTS
from kivy.animation import Animation
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.loadingindicator import MDLoadingIndicator
from kivymd.uix.menu import MDDropdownMenu

import arabic_reshaper
from bidi.algorithm import get_display

ARABIC_SUPPORT = True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "gttst.png")


LANGUAGES = {
    "English": "en",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-CN",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Dutch": "nl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Urdu": "ur",
}


def reshape_arabic(text):
    """إعادة تشكيل النص العربي ليظهر بشكل صحيح."""
    if not ARABIC_SUPPORT:
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped, base_dir="R")


def sanitize_filename(name):
    """تنظيف اسم الملف من الأحرف غير المسموحة."""
    name = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    name = name.replace(" ", "_")
    return name or "voice"


KV = """
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

MDBoxLayout:
    orientation: "vertical"

    canvas.before:
        Color:
            rgba: 0.05, 0.08, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size

    MDTopAppBar:
        title: "GTTS Voice Creator"
        type: "small"
        elevation: 3
        left_action_items: [["microphone", lambda x: None]]
        size_hint_y: None
        height: dp(56)

    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(6)

        canvas.before:
            Color:
                rgba: 0.05, 0.08, 0.15, 0.90
            Rectangle:
                pos: self.pos
                size: self.size

        Image:
            source: app.logo_path
            size_hint_y: None
            height: dp(54)

        Label:
            text: "Text To Speech"
            font_size: sp(22)
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(24)

        Label:
            text: "Text:"
            color: 0.85, 0.90, 1, 1
            size_hint_y: None
            height: dp(18)

        TextInput:
            id: text_input
            size_hint_y: None
            height: dp(105)
            multiline: True
            hint_text: "Type your text here..."
            font_size: sp(18)
            font_name: app.arabic_font
            foreground_color: 1, 1, 1, 1
            hint_text_color: 0.65, 0.72, 0.85, 1
            cursor_color: 0.30, 0.65, 1, 1
            background_color: 0.12, 0.17, 0.28, 1
            padding: [dp(12), dp(10)]
            on_text: app.update_arabic_preview(self.text)

        Label:
            id: arabic_preview
            text: ""
            font_size: sp(17)
            font_name: app.arabic_font
            color: 0.95, 0.95, 1, 1
            halign: "right"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(30)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(6)

            Label:
                text: "Language:"
                color: 0.85, 0.90, 1, 1
                size_hint_x: None
                width: dp(78)

            MDButton:
                id: language_button
                style: "outlined"
                size_hint_x: 1
                on_release: app.open_language_menu(self)
                MDButtonText:
                    id: language_button_text
                    text: app.selected_language

        Label:
            text: "File Name:"
            color: 0.85, 0.90, 1, 1
            size_hint_y: None
            height: dp(18)

        TextInput:
            id: filename_input
            text: "voice"
            size_hint_y: None
            height: dp(38)
            multiline: False
            font_size: sp(16)
            foreground_color: 1, 1, 1, 1
            background_color: 0.12, 0.17, 0.28, 1
            padding: [dp(12), dp(8)]

        AnchorLayout:
            anchor_x: "center"
            size_hint_y: None
            height: dp(42)

            BoxLayout:
                size_hint_x: None
                width: min(dp(260), self.parent.width * 0.92)
                size_hint_y: 1
                spacing: dp(20)

                MDButton:
                    id: generate_button
                    style: "filled"
                    size_hint_x: 3
                    on_release: app.generate_voice()
                    MDButtonText:
                        id: save_button_text
                        text: "Save Voice"

                MDButton:
                    id: play_button
                    style: "tonal"
                    size_hint_x: 4
                    on_release: app.play_voice()
                    MDButtonText:
                        id: play_button_text
                        text: "Play"

        AnchorLayout:
            anchor_x: "center"
            size_hint_y: None
            height: dp(42)

            MDButton:
                id: download_button
                style: "outlined"
                size_hint_x: 1
                size_hint_y: 1
                on_release: app.download_and_open()
                MDButtonText:
                    text: "Download / Open With"

        Label:
            id: status_label
            text: "Ready"
            color: 0.80, 0.86, 1, 1
            halign: "center"
            valign: "middle"
            text_size: self.size
            size_hint_y: None
            height: dp(34)

        MDLoadingIndicator:
            id: progress_spinner
            size_hint: None, None
            size: dp(24), dp(24)
            pos_hint: {"center_x": 0.5}
            active: False

        Label:
            text: "created by Hasan Ibrahem"
            font_size: sp(12)
            color: 0.55, 0.62, 0.75, 1
            halign: "center"
            text_size: self.size
            size_hint_y: None
            height: dp(18)
"""


class TextToSpeechApp(MDApp):
    title = "Text To Speech"
    icon = LOGO_PATH
    language_names = tuple(LANGUAGES.keys())

    def on_start(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        Window.clearcolor = (0.05, 0.08, 0.15, 1)

    def build(self):
        self.sound = None
        self.last_saved_path = None
        self.selected_language = self.language_names[0]
        self.logo_path = LOGO_PATH
        self.arabic_font = "Arial"
        if platform == "win" and os.path.exists(r"C:\Windows\Fonts\arial.ttf"):
            self.arabic_font = r"C:\Windows\Fonts\arial.ttf"

        # اختيار مجلد الحفظ حسب النظام
        if platform == "android":
            self._setup_android_storage()
        else:
            # على الكمبيوتر: حفظ في مجلد Downloads داخل مجلد المستخدم
            home = os.path.expanduser("~")
            self.save_folder = os.path.join(home, "Downloads", "TTS_App")
            os.makedirs(self.save_folder, exist_ok=True)

        root = Builder.load_string(KV)
        self.update_arabic_preview(root.ids.text_input.text, root)
        return root

    def open_language_menu(self, caller):
        items = [
            {
                "text": language,
                "on_release": lambda value=language: self.select_language(value),
            }
            for language in self.language_names
        ]
        MDDropdownMenu(caller=caller, items=items, width=dp(220)).open()

    def select_language(self, language):
        self.selected_language = language
        self.root.ids.language_button_text.text = language

    def update_arabic_preview(self, text, root=None):
        root = root or self.root
        if root is None or "arabic_preview" not in root.ids:
            return

        has_arabic = any("\u0600" <= character <= "\u06ff" for character in text)
        root.ids.arabic_preview.text = reshape_arabic(text) if has_arabic else text

    def _setup_android_storage(self):
        """إعداد مجلد الحفظ في Android داخل مجلد Downloads العام."""
        try:
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                                 Permission.READ_EXTERNAL_STORAGE])
            base = primary_external_storage_path()
            self.save_folder = os.path.join(base, "Download", "TTS_App")
        except Exception:
            # fallback إلى مجلد التطبيق الخاص
            self.save_folder = os.path.join(self.user_data_dir, "TTS_App")
        os.makedirs(self.save_folder, exist_ok=True)

    def set_status(self, message):
        self.root.ids.status_label.text = message

    def set_busy(self, busy):
        self.root.ids.generate_button.disabled = busy
        self.root.ids.play_button.disabled = busy
        self.root.ids.progress_spinner.active = busy
        self.root.ids.save_button_text.text = "Generating..." if busy else "Save Voice"

    def animate_button(self, button_id, color, callback=None):
        button = self.root.ids[button_id]
        normal_color = list(button.md_bg_color)
        Animation.cancel_all(button, "md_bg_color")
        highlight = Animation(md_bg_color=color, duration=0.16, t="out_quad")
        restore = Animation(md_bg_color=normal_color, duration=0.35, t="out_quad")
        sequence = highlight + restore
        if callback:
            sequence.bind(on_complete=lambda *args: callback())
        sequence.start(button)

    def stop_current_sound(self):
        if self.sound:
            try:
                self.sound.stop()
                self.sound.unload()
            except Exception:
                pass
            self.sound = None

    def get_output_path(self):
        """إنشاء مسار الحفظ بناءً على اسم الملف الذي أدخله المستخدم."""
        raw_name = self.root.ids.filename_input.text.strip()
        safe_name = sanitize_filename(raw_name)
        return os.path.join(self.save_folder, f"{safe_name}.mp3")

    def generate_voice(self):
        # استخدم النص الأصلي للصوت؛ إعادة التشكيل مخصصة للعرض فقط
        raw_text = self.root.ids.text_input.text.strip()
        
        language_name = self.selected_language
        language_code = LANGUAGES.get(language_name, "en")

        if not raw_text:
            self.set_status("Please enter some text first.")
            return

        output_path = self.get_output_path()

        self.stop_current_sound()
        self.set_busy(True)
        self.set_status("Creating audio...")

        threading.Thread(
            target=self._generate_voice_thread,
            args=(raw_text, language_code, output_path),
            daemon=True,
        ).start()

    def _generate_voice_thread(self, text, language_code, output_path):
        try:
            tts = gTTS(text=text, lang=language_code)
            tts.save(output_path)
            Clock.schedule_once(lambda dt: self._on_voice_saved(output_path))
        except Exception as error:
            error_message = str(error)
            Clock.schedule_once(lambda dt: self._on_voice_error(error_message))

    def _on_voice_saved(self, path):
        self.last_saved_path = path
        self.set_busy(False)
        filename = os.path.basename(path)
        folder = os.path.dirname(path)
        self.set_status(f"Saved: {filename}\nPath: {folder}")

    def _on_voice_error(self, error_message):
        self.set_busy(False)
        self.set_status("Error: check internet/language.")
        print("TTS error:", error_message)

    def play_voice(self):
        if not self.last_saved_path or not os.path.exists(self.last_saved_path):
            self.set_status("No voice file found. Save it first.")
            return

        self.stop_current_sound()
        self.sound = SoundLoader.load(self.last_saved_path)

        if self.sound:
            self.sound.play()
            self.animate_button("play_button", [0.18, 0.72, 0.35, 1])
            self.set_status("Playing voice...")
        else:
            self.set_status("Could not play audio.")

    def download_and_open(self):
        """فتح الملف بتطبيق خارجي (مشغل موسيقى، إلخ)."""
        if not self.last_saved_path or not os.path.exists(self.last_saved_path):
            self.set_status("No voice file found. Save it first.")
            return

        if platform == "android":
            self.animate_button("download_button", [0.95, 0.68, 0.08, 1])
            self._open_with_android_app()
        else:
            self.animate_button("download_button", [0.95, 0.68, 0.08, 1])
            self._open_with_desktop_app()

    def _open_with_android_app(self):
        """فتح الملف باستخدام Intent على Android."""
        try:
            from android import activity
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            File = autoclass('java.io.File')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            
            context = PythonActivity.mActivity
            file_path = self.last_saved_path
            
            # إنشاء File object
            file = File(file_path)
            
            # الحصول على URI باستخدام FileProvider
            authority = context.getPackageName() + ".fileprovider"
            uri = FileProvider.getUriForFile(context, authority, file)
            
            # إنشاء Intent لفتح الملف
            intent = Intent()
            intent.setAction(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, "audio/mpeg")
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            # بدء النشاط
            context.startActivity(intent)
            
            self.set_status("File opened successfully.")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error opening file: {error_msg}")
            self.set_status(f"Error: {error_msg}")

    def _open_with_desktop_app(self):
        """فتح الملف بالتطبيق الافتراضي على الكمبيوتر."""
        try:
            import subprocess
            import sys
            
            file_path = self.last_saved_path
            
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
            
            self.set_status("File opened successfully.")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error opening file: {error_msg}")
            self.set_status(f"Error: {error_msg}")

    def on_stop(self):
        self.stop_current_sound()


if __name__ == "__main__":
    TextToSpeechApp().run()
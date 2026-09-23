import json
import os
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

DATA_FILE = "alarms.json"


def load_alarms():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_alarms(alarms):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(alarms, f, ensure_ascii=False, indent=2)


class AddAlarmPopup(Popup):
    def __init__(self, on_save, **kwargs):
        super().__init__(**kwargs)
        self.title = "هشدار جدید"
        self.size_hint = (0.9, 0.7)
        self.on_save = on_save

        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.title_input = TextInput(hint_text="عنوان (مثلا: تولد حلما)", multiline=False)
        self.date_input = TextInput(hint_text="تاریخ (مثلا 2026-10-04)", multiline=False)
        self.time_input = TextInput(hint_text="ساعت (مثلا 11:00)", multiline=False)
        self.sound_input = TextInput(hint_text="مسیر فایل صدا (اختیاری)", multiline=False)

        layout.add_widget(Label(text="عنوان هشدار:"))
        layout.add_widget(self.title_input)
        layout.add_widget(Label(text="تاریخ (YYYY-MM-DD):"))
        layout.add_widget(self.date_input)
        layout.add_widget(Label(text="ساعت (HH:MM):"))
        layout.add_widget(self.time_input)
        layout.add_widget(Label(text="صدا (مسیر فایل، بعدا اضافه میشه انتخابگر):"))
        layout.add_widget(self.sound_input)

        save_btn = Button(text="ذخیره", size_hint_y=None, height=50)
        save_btn.bind(on_release=self.save_alarm)
        layout.add_widget(save_btn)

        self.content = layout

    def save_alarm(self, *args):
        title = self.title_input.text.strip()
        date = self.date_input.text.strip()
        time = self.time_input.text.strip()
        sound = self.sound_input.text.strip()

        if not title or not date or not time:
            return  # بعدا پیام خطا اضافه میشه

        try:
            datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            self.title_input.hint_text = "فرمت تاریخ/ساعت اشتباهه!"
            return

        self.on_save({
            "title": title,
            "date": date,
            "time": time,
            "sound": sound or "default",
        })
        self.dismiss()


class AlarmApp(App):
    def build(self):
        self.alarms = load_alarms()

        root = BoxLayout(orientation="vertical")

        header = BoxLayout(size_hint_y=None, height=60, padding=10)
        header.add_widget(Label(text="هشدارهای من", font_size=22))
        add_btn = Button(text="+ افزودن", size_hint_x=0.4)
        add_btn.bind(on_release=self.open_add_popup)
        header.add_widget(add_btn)
        root.add_widget(header)

        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(self.scroll)

        self.refresh_list()
        return root

    def open_add_popup(self, *args):
        popup = AddAlarmPopup(on_save=self.add_alarm)
        popup.open()

    def add_alarm(self, alarm):
        self.alarms.append(alarm)
        save_alarms(self.alarms)
        self.refresh_list()
        # TODO: اینجا باید با pyjnius به AlarmManager اندروید وصل بشیم
        # تا هشدار واقعی (حتی با اپ بسته) زنگ بزنه

    def remove_alarm(self, alarm):
        self.alarms.remove(alarm)
        save_alarms(self.alarms)
        self.refresh_list()

    def refresh_list(self):
        self.list_layout.clear_widgets()
        if not self.alarms:
            self.list_layout.add_widget(Label(text="هنوز هشداری نداری", size_hint_y=None, height=40))
            return

        for alarm in sorted(self.alarms, key=lambda a: (a["date"], a["time"])):
            row = BoxLayout(size_hint_y=None, height=60, padding=5, spacing=10)
            info = f"{alarm['title']}  |  {alarm['date']} {alarm['time']}"
            row.add_widget(Label(text=info))
            del_btn = Button(text="حذف", size_hint_x=0.25)
            del_btn.bind(on_release=lambda x, a=alarm: self.remove_alarm(a))
            row.add_widget(del_btn)
            self.list_layout.add_widget(row)


if __name__ == "__main__":
    AlarmApp().run()


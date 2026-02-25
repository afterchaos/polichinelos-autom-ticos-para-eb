from pynput.keyboard import Controller
from pynput import keyboard
import time
import threading

class AutoTyper:
    def __init__(self):
        self.keyboard_controller = Controller()
        self.is_typing = False

    def type_with_delay(self, text, delay_ms=50, auto_send_enter=True):
        if self.is_typing:
            return
        
        self.is_typing = True
        delay_seconds = delay_ms / 1000.0

        def typing_thread():
            try:
                for char in text:
                    if not self.is_typing:
                        break
                    self.keyboard_controller.type(char)
                    time.sleep(delay_seconds)
                
                if self.is_typing and auto_send_enter:
                    time.sleep(delay_seconds)
                    self.keyboard_controller.press(keyboard.Key.enter)
                    self.keyboard_controller.release(keyboard.Key.enter)
            finally:
                self.is_typing = False

        thread = threading.Thread(target=typing_thread, daemon=True)
        thread.start()

    def stop_typing(self):
        self.is_typing = False

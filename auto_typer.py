import time
import threading
import ctypes
import pyperclip
import random
from pynput.keyboard import Controller, Key
from pynput import keyboard

user32 = ctypes.windll.user32

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    return ""

class AutoTyper:
    # Delay mínimo garantido entre cada tecla. Valores muito baixos fazem o
    # sistema operacional "engolir" a última letra de uma palavra (ex: teclas
    # com Shift, como as letras maiúsculas seguidas de "!") antes que o
    # próximo caractere seja enviado. Esse piso evita o corte de letras
    # (ex: "QUINZE!" virando "QUINZ!" ou "DEZESSEIS!" virando "DEZESEI!").
    MIN_CHAR_DELAY = 0.02
    KEY_HOLD_TIME = 0.015

    # Símbolos que dependem de Shift e sua tecla "base" (sem shift) no layout US
    SHIFT_SYMBOLS = {
        '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '&': '7', '*': '8',
        '(': '9', ')': '0', '_': '-', '+': '=', ':': ';', '"': "'",
        '<': ',', '>': '.', '?': '/', '~': '`', '{': '[', '}': ']', '|': '\\',
    }

    def __init__(self):
        self.keyboard_controller = Controller()
        self.is_typing = False
        self.base_delay = 0.05
        self.initial_window_title = None

    def is_discord_active(self):
        title = get_active_window_title().lower()
        return "discord" in title

    def clear_textbox(self):
        with self.keyboard_controller.pressed(Key.ctrl):
            self.keyboard_controller.press('a')
            self.keyboard_controller.release('a')
        time.sleep(0.05)
        self.keyboard_controller.press(Key.backspace)
        self.keyboard_controller.release(Key.backspace)
        time.sleep(0.1)

    def _type_text_reliably(self, text, char_delay):
        """Digita um texto segurando o Shift continuamente quando necessário,
        em vez de apertar/soltar o Shift a cada caractere.

        Como o texto (ex: números por extenso) é em maiúsculas, ligar e
        desligar o Shift a cada letra pode fazer jogos que leem teclado via
        polling/raw input (como o Roblox) perder justamente a tecla na hora
        da troca — cortando sempre a letra logo antes do "!". Mantendo o
        Shift pressionado do início ao fim do texto, essa troca some.
        """
        needs_shift = any(c.isalpha() or c in self.SHIFT_SYMBOLS for c in text)
        if needs_shift:
            self.keyboard_controller.press(Key.shift)
            time.sleep(self.KEY_HOLD_TIME)
        try:
            for char in text:
                if not self.is_typing:
                    break
                if char == ' ':
                    base_key = Key.space
                elif char.isalpha():
                    base_key = char.lower()
                else:
                    base_key = self.SHIFT_SYMBOLS.get(char, char)
                self.keyboard_controller.press(base_key)
                time.sleep(self.KEY_HOLD_TIME)
                self.keyboard_controller.release(base_key)
                time.sleep(char_delay)
        finally:
            if needs_shift:
                time.sleep(self.KEY_HOLD_TIME)
                self.keyboard_controller.release(Key.shift)

    def type_with_protections(self, text, delay_ms=50, auto_send_enter=True, random_extra=True):
        if self.is_typing:
            return
        
        self.is_typing = True
        self.base_delay = delay_ms / 1000.0
        
        def typing_thread():
            try:
                # Limpa a caixa de texto antes de começar
                self.clear_textbox()

                # Digita o texto inteiro mantendo o Shift seguro do início ao fim
                final_delay = max(self.base_delay, self.MIN_CHAR_DELAY)
                if random_extra:
                    final_delay += random.uniform(0, 0.05)
                self._type_text_reliably(text, final_delay)
                
                # Enviar mensagem
                if self.is_typing and auto_send_enter:
                    time.sleep(max(self.base_delay, self.MIN_CHAR_DELAY))
                    self.keyboard_controller.press(Key.enter)
                    time.sleep(self.KEY_HOLD_TIME)
                    self.keyboard_controller.release(Key.enter)

            except Exception as e:
                print(f"Erro inesperado ao digitar: {e}")
            finally:
                self.is_typing = False

        thread = threading.Thread(target=typing_thread, daemon=True)
        thread.start()

    def type_with_delay(self, text, delay_ms=50, auto_send_enter=True):
        """Helper compatível com o fluxo de auto-typing."""
        self.type_with_protections(text, delay_ms, auto_send_enter, random_extra=False)

    def stop_typing(self):
        self.is_typing = False
        self.initial_window_title = None

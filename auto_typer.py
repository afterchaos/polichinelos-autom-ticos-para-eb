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
    def __init__(self):
        self.keyboard_controller = Controller()
        self.is_typing = False
        self.fail_count = 0
        self.max_fails = 3
        self.base_delay = 0.05
        self.adaptive_delay = 0.0
        self.initial_window_title = None
        self.on_pause_callback = None

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

    def check_message_sent(self):
        """Verifica se a caixa está vazia após enviar mensagem"""
        try:
            time.sleep(0.25)  # Espera mais tempo pro Discord processar e limpar a caixa
            
            # Apenas seleciona tudo e tenta copiar
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('a')
                self.keyboard_controller.release('a')
                time.sleep(0.03)
                self.keyboard_controller.press('c')
                self.keyboard_controller.release('c')
            
            time.sleep(0.1)
            
            # Lê o conteúdo da caixa
            clipboard_content = pyperclip.paste().strip()
            
            # Se está vazio = mensagem foi enviada com sucesso!
            if clipboard_content == "":
                return True
            
            # Se tem conteúdo = mensagem não foi enviada
            return False
            
        except Exception as e:
            print(f"Erro ao verificar envio: {e}")
            # Em caso de erro, assume sucesso
            return True

    def verify_textbox_exists(self):
        """Verifica se o campo de texto está presente de forma rápida e confiável"""
        if not self.is_discord_active():
            return False

        old_clip = pyperclip.paste()
        marker = f"V_{random.randint(10, 99)}"
        pyperclip.copy("VOID")

        try:
            # 1. Digita o marcador
            self.keyboard_controller.type(marker)
            time.sleep(0.05)

            # 2. Tenta selecionar e copiar o marcador
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('a')
                self.keyboard_controller.release('a')
                time.sleep(0.05)
                self.keyboard_controller.press('c')
                self.keyboard_controller.release('c')

            time.sleep(0.1)
            res = pyperclip.paste()

            # 3. Limpa obrigatoriamente o marcador completo
            for _ in range(len(marker)):
                self.keyboard_controller.press(Key.backspace)
                self.keyboard_controller.release(Key.backspace)
                time.sleep(0.01)

            success = (res == marker)
            return success
        finally:
            pyperclip.copy(old_clip)

    def has_editable_textbox(self):
        """Retorna True quando o Discord ainda está com um campo de texto livre e utilizável."""
        try:
            return self.is_discord_active() and self.verify_textbox_exists()
        except Exception:
            return False

    def type_with_protections(self, text, delay_ms=50, auto_send_enter=True, random_extra=True):
        if self.is_typing:
            return
        
        self.is_typing = True
        self.base_delay = delay_ms / 1000.0
        
        def typing_thread():
            try:
                # 1. Verificar se Discord está ativo
                if not self.is_discord_active():
                    self.pause_and_notify("Discord não é a janela ativa.")
                    return

                # 2. Registrar o título da janela inicial (canal)
                if self.initial_window_title is None:
                    self.initial_window_title = get_active_window_title()

                # 3. Verificar se o canal mudou
                current_title = get_active_window_title()
                if current_title != self.initial_window_title:
                    self.pause_and_notify(f"Canal mudou ou interface alterada: {current_title}")
                    return

                # 4. Limpar caixa de texto antes de começar
                self.clear_textbox()

                # 5. Digitar com delays
                for char in text:
                    if not self.is_typing:
                        break
                    self.keyboard_controller.type(char)
                    
                    final_delay = self.base_delay + self.adaptive_delay
                    if random_extra:
                        final_delay += random.uniform(0, 0.05)
                    
                    time.sleep(final_delay)
                
                # 6. Enviar mensagem
                if self.is_typing and auto_send_enter:
                    time.sleep(self.base_delay)
                    self.keyboard_controller.press(Key.enter)
                    self.keyboard_controller.release(Key.enter)
                    
                    # Esperar um pouco para o Discord processar
                    time.sleep(0.5)
                    
                    # 7. Confirmar envio (se a caixa ficou vazia)
                    if not self.check_message_sent():
                        self.fail_count += 1
                        self.adaptive_delay += 0.5 # Aumenta delay se falhar (Slow mode/Timeout)
                        
                        if self.fail_count >= self.max_fails:
                            self.pause_and_notify("Falha repetida no envio (Timeout/Permissões/Slowmode).")
                        else:
                            # Tenta limpar para a próxima
                            self.clear_textbox()
                    else:
                        # Sucesso
                        self.fail_count = 0
                        # Reduz gradualmente o delay adaptativo se estava alto
                        if self.adaptive_delay > 0:
                            self.adaptive_delay = max(0, self.adaptive_delay - 0.1)

            except Exception as e:
                self.pause_and_notify(f"Erro inesperado: {str(e)}")
            finally:
                self.is_typing = False

        thread = threading.Thread(target=typing_thread, daemon=True)
        thread.start()

    def type_with_delay(self, text, delay_ms=50, auto_send_enter=True):
        """Helper compatível com o fluxo de auto-typing."""
        self.type_with_protections(text, delay_ms, auto_send_enter, random_extra=False)

    def pause_and_notify(self, reason):
        self.is_typing = False
        print(f"PAUSE: {reason}")
        if self.on_pause_callback:
            self.on_pause_callback(reason)

    def stop_typing(self):
        self.is_typing = False
        self.initial_window_title = None

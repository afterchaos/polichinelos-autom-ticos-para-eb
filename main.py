import customtkinter as ctk
import pyperclip
from pynput import keyboard
from pynput.keyboard import Controller
import threading
import time

# Configurações do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoJJSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AUTO JJS")
        self.geometry("800x600")
        self.resizable(False, False)
        

        # Variáveis
        self.start_num = 1
        self.end_num = 10000
        self.contador = self.start_num
        self.trigger_key_str = "TAB"
        self.trigger_key_obj = keyboard.Key.tab
        self.listening_for_key = False
        self.is_running = False
        self.keyboard_controller = Controller()
        self.exclamation_format = "junta"  # "junta" ou "separada"

        # Cores Customizáveis
        self.color_main = "#7289da"
        self.color_btn_primary = "#5865f2"
        self.color_btn_success = "#43b581"
        self.color_btn_danger = "#f04747"
        self.color_card_bg = "#2b2d31"
        
        # Dicionários para conversão
        self.unidades = ['', 'UM', 'DOIS', 'TRÊS', 'QUATRO', 'CINCO', 'SEIS', 'SETE', 'OITO', 'NOVE']
        self.dezenas = ['', '', 'VINTE', 'TRINTA', 'QUARENTA', 'CINQUENTA', 'SESSENTA', 'SETENTA', 'OITENTA', 'NOVENTA']
        self.teenagers = ['DEZ', 'ONZE', 'DOZE', 'TREZE', 'QUATORZE', 'QUINZE', 'DEZESSEIS', 'DEZESSETE', 'DEZOITO', 'DEZENOVE']
        self.centenas = ['', 'CENTO', 'DUZENTOS', 'TREZENTOS', 'QUATROCENTOS', 'QUINHENTOS', 'SEISCENTOS', 'SETECENTOS', 'OITOCENTOS', 'NOVECENTOS']
        self.escala = ['', 'MIL', 'MILHÃO', 'BILHÃO']

        self.setup_ui()
        self.start_keyboard_listener()
        
        # Bind para clicar fora dos campos
        self.bind("<Button-1>", self.on_window_click)

    def on_window_click(self, event):
        # Se o widget clicado não for um dos campos de entrada, remove o foco
        try:
            if event.widget != self.start_entry._entry and event.widget != self.end_entry._entry:
                self.focus()
        except:
            self.focus()

    def setup_ui(self):
        # Frame Lateral (Simulado pela imagem)
        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo no frame lateral
        self.logo_label = ctk.CTkLabel(self.sidebar, text="", font=("Segoe UI", 24))
        self.logo_label.pack(pady=20)
        
        # Divider
        self.divider = ctk.CTkFrame(self.sidebar, height=2, width=30)
        self.divider.pack(pady=10)

        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True, padx=40, pady=20)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="⚡ AUTO JJS", font=("Segoe UI Bold", 32))
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="⌨ Configure os limites e a tecla de acionamento abaixo", 
                                         font=("Segoe UI", 14), text_color="gray")
        self.subtitle_label.pack(anchor="w")

        # Config Settings Frame
        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.settings_frame.pack(fill="x", pady=(0, 10))

        # Start Num
        self.start_label = ctk.CTkLabel(self.settings_frame, text="Início:", font=("Segoe UI Bold", 12))
        self.start_label.pack(side="left", padx=(0, 5))
        self.start_entry = ctk.CTkEntry(self.settings_frame, width=80)
        self.start_entry.insert(0, str(self.start_num))
        self.start_entry.pack(side="left", padx=(0, 10))

        # End Num
        self.end_label = ctk.CTkLabel(self.settings_frame, text="Fim:", font=("Segoe UI Bold", 12))
        self.end_label.pack(side="left", padx=(0, 5))
        self.end_entry = ctk.CTkEntry(self.settings_frame, width=80)
        self.end_entry.insert(0, str(self.end_num))
        self.end_entry.pack(side="left", padx=(0, 10))

        # Trigger Key
        self.key_label = ctk.CTkLabel(self.settings_frame, text="Tecla:", font=("Segoe UI Bold", 12))
        self.key_label.pack(side="left", padx=(0, 5))
        self.key_btn = ctk.CTkButton(self.settings_frame, text=self.trigger_key_str, 
                                           width=100, command=self.start_key_capture)
        self.key_btn.pack(side="left", padx=(0, 10))

        # Apply Button
        self.btn_apply = ctk.CTkButton(self.settings_frame, text="APLICAR", width=80, fg_color=self.color_btn_primary, 
                                      hover_color=self.color_btn_primary, font=("Segoe UI Bold", 12), command=self.apply_settings)
        self.btn_apply.pack(side="left", padx=(0, 10))

        # Start/Stop Button
        self.btn_toggle = ctk.CTkButton(self.settings_frame, text="ATIVAR", width=100, fg_color=self.color_btn_success, 
                                       hover_color=self.color_btn_success, font=("Segoe UI Bold", 12), command=self.toggle_status)
        self.btn_toggle.pack(side="left", padx=(0, 10))

        # Exclamation Toggle Button (next to ATIVAR)
        self.exclamation_btn = ctk.CTkButton(self.settings_frame, text="JUNTA", width=100, 
                                           fg_color=self.color_btn_primary, hover_color=self.color_btn_primary, 
                                           font=("Segoe UI Bold", 12), corner_radius=8,
                                           command=self.toggle_exclamation_format)
        self.exclamation_btn.pack(side="left", padx=(0, 10))

        # Display Card
        self.card = ctk.CTkFrame(self.main_container, height=300, corner_radius=15, fg_color=self.color_card_bg)
        self.card.pack(fill="x", pady=20)
        self.card.pack_propagate(False)

        self.number_label = ctk.CTkLabel(self.card, text="1", font=("Segoe UI Bold", 120), text_color=self.color_main)
        self.number_label.pack(expand=True, pady=(40, 0))

        self.text_label = ctk.CTkLabel(self.card, text="UM!", font=("Segoe UI Bold", 24))
        self.text_label.pack(expand=True, pady=(0, 40))

        # Progress Bar and Counter
        self.progress_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.progress_frame.pack(fill="x", side="bottom", padx=40, pady=20)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=10, progress_color="#43444b")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(1/10000)

        self.counter_label = ctk.CTkLabel(self.progress_frame, text="1 / 10.000", font=("Segoe UI", 12), text_color="gray")
        self.counter_label.pack()

        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=20)

        self.btn_prev = ctk.CTkButton(self.buttons_frame, text="← ANTERIOR", fg_color=self.color_btn_danger, hover_color=self.color_btn_danger, 
                                    font=("Segoe UI Bold", 14), height=50, command=self.prev_number)
        self.btn_prev.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_next = ctk.CTkButton(self.buttons_frame, text="PRÓXIMO →", fg_color=self.color_btn_primary, hover_color=self.color_btn_primary, 
                                    font=("Segoe UI Bold", 14), height=50, command=self.next_number)
        self.btn_next.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_reset = ctk.CTkButton(self.buttons_frame, text="↻ RESETAR", fg_color="#36393f", hover_color="#2f3136", 
                                     font=("Segoe UI Bold", 14), height=50, command=self.reset_number)
        self.btn_reset.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_copy = ctk.CTkButton(self.buttons_frame, text="📋 COPIAR", fg_color=self.color_btn_success, hover_color=self.color_btn_success, 
                                    font=("Segoe UI Bold", 14), height=50, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=5, expand=True, fill="x")

        # Footer
        self.footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.footer_frame.pack(fill="x", side="bottom")

        self.footer_hint = ctk.CTkLabel(self.footer_frame, text=f"💡 Pressione {self.trigger_key_str} para avançar", font=("Segoe UI", 12), text_color=self.color_main)
        self.footer_hint.pack(side="left")

        # Watermark
        self.watermark_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.watermark_frame.place(relx=0.98, rely=0.99, anchor="se")
        
        self.by_label = ctk.CTkLabel(self.watermark_frame, text="by: ", font=("Segoe UI Bold", 13), text_color="gray")
        self.by_label.pack(side="left")
        
        self.name_label = ctk.CTkLabel(self.watermark_frame, text="witheringfeelings", font=("Segoe UI Bold", 13), text_color="#0096FF")
        self.name_label.pack(side="left")
        
        self.watermark_frame.lift()

        self.update_display()

    def prev_number(self):
        if self.contador > self.start_num:
            self.contador -= 1
            self.update_display()

    # Funções de Conversão (do script.py)
    def converter_grupo(self, num):
        if num == 0: return ''
        resultado = []
        c = num // 100
        if c > 0:
            resultado.append('CENTO' if c == 1 and num % 100 > 0 else self.centenas[c])
            if c == 1 and num % 100 == 0: resultado[-1] = "CEM"
        
        resto = num % 100
        if resto > 0:
            if c > 0: resultado.append('E')
            if 10 <= resto <= 19:
                resultado.append(self.teenagers[resto - 10])
            else:
                d = resto // 10
                u = resto % 10
                if d > 0:
                    resultado.append(self.dezenas[d])
                    if u > 0:
                        resultado.append('E')
                        resultado.append(self.unidades[u])
                elif u > 0:
                    resultado.append(self.unidades[u])
        return ' '.join(resultado)

    def numero_para_extenso(self, num):
        if num == 0: return 'ZERO'
        
        grupos = []
        escala_idx = 0
        temp_num = num
        while temp_num > 0:
            grupo = temp_num % 1000
            if grupo != 0:
                texto_grupo = self.converter_grupo(grupo)
                if escala_idx == 1:
                    if grupo == 1: 
                        texto_grupo = 'MIL'
                    else: 
                        texto_grupo += ' MIL'
                grupos.append(texto_grupo)
            temp_num //= 1000
            escala_idx += 1
        
        grupos.reverse()
        
        # Para números com milhares e parte restante, adicionar "E" entre eles
        # "E" para: 1-99 (unidades/dezenas) ou múltiplos de 100 (200, 300... 900)
        if len(grupos) == 2 and (grupos[0].endswith(' MIL') or grupos[0] == 'MIL'):
            resto = num % 1000
            if resto > 0:
                # Adiciona "E" para restos 1-99 ou centenas redondas (100, 200, 300...)
                if resto < 100 or resto % 100 == 0:
                    return grupos[0] + ' E ' + grupos[1]
        
        resultado = ' '.join(grupos).strip()
        return resultado

    def start_key_capture(self):
        self.listening_for_key = True
        self.key_btn.configure(text="AGUARDANDO...")

    def format_key_name(self, key):
        if hasattr(key, 'name'):
            return key.name.upper()
        elif hasattr(key, 'char'):
            if key.char:
                return key.char.upper()
        return str(key).replace("'", "").upper()

    def toggle_status(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_toggle.configure(text="DESATIVAR", fg_color=self.color_btn_danger, hover_color=self.color_btn_danger)
        else:
            self.btn_toggle.configure(text="ATIVAR", fg_color=self.color_btn_success, hover_color=self.color_btn_success)

    def apply_settings(self):
        try:
            new_start = int(self.start_entry.get())
            new_end = int(self.end_entry.get())
            
            if new_start >= new_end:
                return

            self.start_num = new_start
            self.end_num = new_end
            
            # Se o contador atual estiver fora do novo intervalo, ajusta ele
            if self.contador < self.start_num:
                self.contador = self.start_num
            elif self.contador > self.end_num:
                self.contador = self.end_num
                
            self.update_display()
            
            # Tira o foco dos campos de entrada
            self.focus()
        except ValueError:
            pass

    def update_display(self):
        texto = self.numero_para_extenso(self.contador)
        self.number_label.configure(text=str(self.contador))
        if self.exclamation_format == "junta":
            self.text_label.configure(text=texto + "!")
        else:
            self.text_label.configure(text=texto + " !")
        
        # Formata o texto do contador com os novos limites
        self.counter_label.configure(text=f"{self.contador:,} / {self.end_num:,}".replace(',', '.'))
        
        # Ajusta a barra de progresso baseada no intervalo
        total_range = self.end_num - self.start_num
        if total_range > 0:
            progress = (self.contador - self.start_num) / total_range
            self.progress_bar.set(max(0.01, progress)) # Garante um mínimo de visibilidade
        else:
            self.progress_bar.set(1.0)

    def next_number(self):
        if self.contador < self.end_num:
            self.contador += 1
            self.update_display()

    def prev_number(self):
        if self.contador > self.start_num:
            self.contador -= 1
            self.update_display()

    def reset_number(self):
        self.contador = self.start_num
        self.update_display()

    def toggle_exclamation_format(self):
        if self.exclamation_format == "junta":
            self.exclamation_format = "separada"
            self.exclamation_btn.configure(text="SEPARADA", fg_color="#36393f", hover_color="#2f3136")
        else:
            self.exclamation_format = "junta"
            self.exclamation_btn.configure(text="JUNTA", fg_color=self.color_btn_primary, hover_color=self.color_btn_primary)
        
        self.update_display()

    def get_formatted_text(self):
        texto = self.numero_para_extenso(self.contador)
        if self.exclamation_format == "junta":
            return texto + "!"
        else:
            return texto + " !"

    def copy_to_clipboard(self):
        texto = self.get_formatted_text()
        pyperclip.copy(texto)

    # Keyboard Listener
    def start_keyboard_listener(self):
        def on_press(key):
            if self.listening_for_key:
                self.trigger_key_obj = key
                self.trigger_key_str = self.format_key_name(key)
                self.listening_for_key = False
                
                # Atualiza UI com o novo nome da tecla
                self.after(0, lambda: self.key_btn.configure(text=self.trigger_key_str))
                self.after(0, lambda: self.footer_hint.configure(text=f"💡 Pressione {self.trigger_key_str} para avançar"))
                return

            if key == self.trigger_key_obj and self.is_running:
                # Usar after para interagir com a UI de forma segura
                self.after(0, self.auto_type_and_advance)

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def auto_type_and_advance(self):
        texto = self.get_formatted_text()
        self.keyboard_controller.type(texto)
        self.next_number()

if __name__ == "__main__":
    app = AutoJJSApp()
    app.mainloop()
 
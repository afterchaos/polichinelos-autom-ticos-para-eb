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
        self.contador = 1
        self.keyboard_controller = Controller()
        
        # Dicionários para conversão
        self.unidades = ['', 'UM', 'DOIS', 'TRÊS', 'QUATRO', 'CINCO', 'SEIS', 'SETE', 'OITO', 'NOVE']
        self.dezenas = ['', '', 'VINTE', 'TRINTA', 'QUARENTA', 'CINQUENTA', 'SESSENTA', 'SETENTA', 'OITENTA', 'NOVENTA']
        self.teenagers = ['DEZ', 'ONZE', 'DOZE', 'TREZE', 'QUATORZE', 'QUINZE', 'DEZESSEIS', 'DEZESSETE', 'DEZOITO', 'DEZENOVE']
        self.centenas = ['', 'CENTO', 'DUZENTOS', 'TREZENTOS', 'QUATROCENTOS', 'QUINHENTOS', 'SEISCENTOS', 'SETECENTOS', 'OITOCENTOS', 'NOVECENTOS']
        self.escala = ['', 'MIL', 'MILHÃO', 'BILHÃO']

        self.setup_ui()
        self.start_keyboard_listener()

    def setup_ui(self):
        # Frame Lateral (Simulado pela imagem)
        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo no frame lateral
        self.logo_label = ctk.CTkLabel(self.sidebar, text="⚡", font=("Segoe UI", 24))
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
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="⌨ Pressione TAB para avançar | Clique nos botões para controlar", 
                                         font=("Segoe UI", 14), text_color="gray")
        self.subtitle_label.pack(anchor="w")

        # Display Card
        self.card = ctk.CTkFrame(self.main_container, height=300, corner_radius=15, fg_color="#2b2d31")
        self.card.pack(fill="x", pady=20)
        self.card.pack_propagate(False)

        self.number_label = ctk.CTkLabel(self.card, text="1", font=("Segoe UI Bold", 120), text_color="#7289da")
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

        self.btn_prev = ctk.CTkButton(self.buttons_frame, text="← ANTERIOR", fg_color="#f04747", hover_color="#d84040", 
                                    font=("Segoe UI Bold", 14), height=50, command=self.prev_number)
        self.btn_prev.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_next = ctk.CTkButton(self.buttons_frame, text="PRÓXIMO →", fg_color="#5865f2", hover_color="#4752c4", 
                                    font=("Segoe UI Bold", 14), height=50, command=self.next_number)
        self.btn_next.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_reset = ctk.CTkButton(self.buttons_frame, text="↻ RESETAR", fg_color="#36393f", hover_color="#2f3136", 
                                     font=("Segoe UI Bold", 14), height=50, command=self.reset_number)
        self.btn_reset.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_copy = ctk.CTkButton(self.buttons_frame, text="📋 COPIAR", fg_color="#43b581", hover_color="#3ca374", 
                                    font=("Segoe UI Bold", 14), height=50, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=5, expand=True, fill="x")

        # Footer
        self.footer_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.footer_frame.pack(fill="x", side="bottom")

        self.footer_hint = ctk.CTkLabel(self.footer_frame, text="💡 Pressione TAB para avançar", font=("Segoe UI", 12), text_color="#7289da")
        self.footer_hint.pack(side="left")

        self.footer_author = ctk.CTkLabel(self.footer_frame, text="by witheringfeelings", font=("Segoe UI", 10), text_color="gray")
        self.footer_author.pack(side="right")

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
        if num == 1000: return 'MIL'
        if num == 10000: return 'DEZ MIL'
        
        grupos = []
        escala_idx = 0
        temp_num = num
        while temp_num > 0:
            grupo = temp_num % 1000
            if grupo != 0:
                texto_grupo = self.converter_grupo(grupo)
                if escala_idx == 1:
                    if grupo == 1: texto_grupo = 'MIL'
                    else: texto_grupo += ' MIL'
                grupos.append(texto_grupo)
            temp_num //= 1000
            escala_idx += 1
        
        grupos.reverse()
        return ' E '.join(grupos).replace('MIL E ', 'MIL ').strip()

    def update_display(self):
        texto = self.numero_para_extenso(self.contador)
        self.number_label.configure(text=str(self.contador))
        self.text_label.configure(text=texto + "!")
        self.counter_label.configure(text=f"{self.contador:,} / 10.000".replace(',', '.'))
        self.progress_bar.set(self.contador / 10000)

    def next_number(self):
        if self.contador < 10000:
            self.contador += 1
            self.update_display()

    def prev_number(self):
        if self.contador > 1:
            self.contador -= 1
            self.update_display()

    def reset_number(self):
        self.contador = 1
        self.update_display()

    def copy_to_clipboard(self):
        texto = self.numero_para_extenso(self.contador) + "!"
        pyperclip.copy(texto)

    # Keyboard Listener
    def start_keyboard_listener(self):
        def on_press(key):
            if key == keyboard.Key.tab:
                # Usar after para interagir com a UI de forma segura
                self.after(0, self.auto_type_and_advance)

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def auto_type_and_advance(self):
        texto = self.numero_para_extenso(self.contador) + "!"
        # Pequeno delay para não interferir com o TAB pressionado
        time.sleep(0.1)
        self.keyboard_controller.type(texto)
        self.next_number()

if __name__ == "__main__":
    app = AutoJJSApp()
    app.mainloop()

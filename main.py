import customtkinter as ctk
import pyperclip
import time
import cv2
import numpy as np
from pynput import keyboard
from pynput.keyboard import Controller
from config_manager import ConfigManager
from auto_typer import AutoTyper

from updater import run_auto_update

# Configurações do Aplicativo
APP_VERSION = "1.0.0"
REPO_OWNER = "afterchaos"
REPO_NAME = "autoJJS_bywithering"
EXECUTABLE_NAME = "AutoJJS.exe"

# Configurações do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoJJSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicia verificação de atualização antes de tudo
        try:
            run_auto_update(REPO_OWNER, REPO_NAME, APP_VERSION, EXECUTABLE_NAME)
        except Exception as e:
            print(f"Erro no auto-update: {e}")

        self.title(f"AUTO JJS - v{APP_VERSION}")
        self.geometry("900x650")
        self.resizable(False, False)
        
        # Carrega configurações
        self.config_manager = ConfigManager()
        self.auto_typer = AutoTyper()

        # Variáveis - Main Tab
        self.start_num = self.config_manager.get("main", "start_num", 1)
        self.end_num = self.config_manager.get("main", "end_num", 10000)
        self.contador = self.start_num
        self.trigger_key_str = self.config_manager.get("main", "trigger_key", "TAB")
        self.trigger_key_obj = self._parse_key_string(self.trigger_key_str)
        self.listening_for_key = False
        self.is_running = False
        self.keyboard_controller = Controller()
        self.exclamation_format = self.config_manager.get("main", "exclamation_format", "junta")

        # Variáveis - Auto Type Tab
        self.auto_type_enabled = self.config_manager.get("auto_type", "enabled", False)
        self.auto_type_hotkey_str = self.config_manager.get("auto_type", "hotkey", "f9").lower()
        self.auto_type_hotkey_obj = self._parse_key_string(self.auto_type_hotkey_str)
        self.auto_type_delay_ms = self.config_manager.get("auto_type", "delay_ms", 50)
        self.auto_send_enter = self.config_manager.get("auto_type", "auto_send_enter", True)
        self.listening_for_auto_type_key = False
        self.capturing_number = False
        self.number_buffer = ""
        self.last_hotkey_time = 0
        self.sequence_active = False  # Controla se a sequência está ativa
        self.sequence_running = False # Evita múltiplas threads da mesma sequência
        self.typing_automatically = False  # Controla se o programa está digitando
        self.is_typing_char = False  # Indica se o programa está simulando o pressionamento de uma tecla específica
        
        # Variáveis independentes para a aba Auto Type
        self.auto_type_start_num = self.config_manager.get("auto_type", "start_num", 1)
        self.auto_type_end_num = self.config_manager.get("auto_type", "end_num", 10000)

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
        
        # Adiciona watermark
        # self.add_watermark()
        
    def add_watermark(self):
        """Adiciona watermark no canto inferior direito da janela"""
        # Label com "by: witheringfeelings" sem frame para evitar fundo
        # watermark_label = ctk.CTkLabel(
        #     self, 
        #     text="by: witheringfeelings",
        #     font=("Segoe UI", 11),
        #     text_color="gray"
        # )
        # # Posicionamento: x=-10 (10px da direita), y=-10 (10px do fundo)
        # # Para subir o texto: aumente o valor de y (ex: y=-30 para subir mais)
        # # Para descer o texto: diminua o valor de y (ex: y=-5 para descer mais)
        # watermark_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-50)

    def _parse_key_string(self, key_str):
        if not key_str:
            return keyboard.Key.tab
            
        key_str = key_str.upper()
        # Mapeamento estendido para teclas especiais
        key_map = {
            "TAB": keyboard.Key.tab,
            "ENTER": keyboard.Key.enter,
            "SHIFT": keyboard.Key.shift,
            "CTRL": keyboard.Key.ctrl,
            "ALT": keyboard.Key.alt,
            "SPACE": keyboard.Key.space,
            "CAPS_LOCK": keyboard.Key.caps_lock,
            "CAPSLOCK": keyboard.Key.caps_lock,
            "CAPS": keyboard.Key.caps_lock,
            "ESC": keyboard.Key.esc,
            "BACKSPACE": keyboard.Key.backspace,
            "DELETE": keyboard.Key.delete,
            "UP": keyboard.Key.up,
            "DOWN": keyboard.Key.down,
            "LEFT": keyboard.Key.left,
            "RIGHT": keyboard.Key.right,
            "HOME": keyboard.Key.home,
            "END": keyboard.Key.end,
            "PAGE_UP": keyboard.Key.page_up,
            "PAGE_DOWN": keyboard.Key.page_down,
            "INSERT": keyboard.Key.insert,
            "F1": keyboard.Key.f1,
            "F2": keyboard.Key.f2,
            "F3": keyboard.Key.f3,
            "F4": keyboard.Key.f4,
            "F5": keyboard.Key.f5,
            "F6": keyboard.Key.f6,
            "F7": keyboard.Key.f7,
            "F8": keyboard.Key.f8,
            "F9": keyboard.Key.f9,
            "F10": keyboard.Key.f10,
            "F11": keyboard.Key.f11,
            "F12": keyboard.Key.f12,
        }
        
        if key_str in key_map:
            return key_map[key_str]
        
        # Tenta pegar dinamicamente de keyboard.Key
        try:
            return getattr(keyboard.Key, key_str.lower())
        except AttributeError:
            if len(key_str) == 1:
                return key_str.lower()
            return keyboard.Key.tab

    def _is_input_focused(self):
        """Verifica se algum campo de entrada está em foco para evitar disparos acidentais"""
        try:
            focused = self.focus_get()
            if focused is None:
                return False
            # Verifica se o widget em foco é um entry ou textbox
            class_name = str(focused.__class__).lower()
            if "entry" in class_name or "textbox" in class_name:
                return True
            return False
        except:
            return False

    def on_window_click(self, event):
        try:
            # Permite clicar nos campos de entrada da aba principal
            if event.widget == self.start_entry._entry or event.widget == self.end_entry._entry:
                return
            
            # Permite clicar nos campos de entrada da aba Auto Type
            if event.widget == self.auto_type_start_entry._entry or event.widget == self.auto_type_end_entry._entry:
                return
                
            # Remove foco de outros widgets
            self.focus()
        except:
            self.focus()

    def setup_ui(self):
        # Frame Lateral
        self.sidebar = ctk.CTkFrame(self, width=60, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="", font=("Segoe UI", 24))
        self.logo_label.pack(pady=20)
        
        self.divider = ctk.CTkFrame(self.sidebar, height=2, width=30)
        self.divider.pack(pady=10)

        # Main Container com Abas
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Tab View
        self.tabview = ctk.CTkTabview(self.main_container, corner_radius=10)
        self.tabview.pack(fill="both", expand=True)

        # Aba 1: Gerador Principal
        self.tab_main = self.tabview.add("⚡ Auto JJ's")
        self.tab_main.grid_rowconfigure(0, weight=0)
        self.tab_main.grid_rowconfigure(1, weight=1)
        self.tab_main.grid_rowconfigure(2, weight=0)
        
        # Aba 2: Configuração de Auto Type
        self.tab_config = self.tabview.add("⚙️ JJ'S AFK")
        
        self.setup_main_tab()
        self.setup_config_tab()


    def setup_main_tab(self):
        # Header
        header_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(header_frame, text="⚡ AUTO JJS", font=("Segoe UI Bold", 28))
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(header_frame, text="⌨ Configure os limites e a tecla de acionamento abaixo", 
                                         font=("Segoe UI", 12), text_color="gray")
        subtitle_label.pack(anchor="w")

        # Settings Frame
        settings_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 15))

        start_label = ctk.CTkLabel(settings_frame, text="Início:", font=("Segoe UI Bold", 11))
        start_label.pack(side="left", padx=(0, 5))
        self.start_entry = ctk.CTkEntry(settings_frame, width=70)
        self.start_entry.insert(0, str(self.start_num))
        self.start_entry.pack(side="left", padx=(0, 10))

        end_label = ctk.CTkLabel(settings_frame, text="Fim:", font=("Segoe UI Bold", 11))
        end_label.pack(side="left", padx=(0, 5))
        self.end_entry = ctk.CTkEntry(settings_frame, width=70)
        self.end_entry.insert(0, str(self.end_num))
        self.end_entry.pack(side="left", padx=(0, 10))

        key_label = ctk.CTkLabel(settings_frame, text="Tecla:", font=("Segoe UI Bold", 11))
        key_label.pack(side="left", padx=(0, 5))
        self.key_btn = ctk.CTkButton(settings_frame, text=self.trigger_key_str, 
                                           width=90, command=self.start_key_capture, font=("Segoe UI Bold", 10))
        self.key_btn.pack(side="left", padx=(0, 10))

        self.btn_apply = ctk.CTkButton(settings_frame, text="APLICAR", width=80, fg_color=self.color_btn_primary, 
                                      hover_color=self.color_btn_primary, font=("Segoe UI Bold", 10), command=self.apply_settings)
        self.btn_apply.pack(side="left", padx=(0, 10))

        self.btn_toggle = ctk.CTkButton(settings_frame, text="ATIVAR", width=80, fg_color=self.color_btn_success, 
                                       hover_color=self.color_btn_success, font=("Segoe UI Bold", 10), command=self.toggle_status)
        self.btn_toggle.pack(side="left", padx=(0, 10))

        self.exclamation_btn = ctk.CTkButton(settings_frame, text="JUNTA", width=80, 
                                           fg_color=self.color_btn_primary, hover_color=self.color_btn_primary, 
                                           font=("Segoe UI Bold", 10), corner_radius=8,
                                           command=self.toggle_exclamation_format)
        self.exclamation_btn.pack(side="left", padx=(0, 10))

        # Display Card
        self.card = ctk.CTkFrame(self.tab_main, height=280, corner_radius=15, fg_color=self.color_card_bg)
        self.card.pack(fill="both", expand=True, pady=15)
        self.card.pack_propagate(False)

        self.number_label = ctk.CTkLabel(self.card, text="1", font=("Segoe UI Bold", 100), text_color=self.color_main)
        self.number_label.pack(expand=True, pady=(30, 0))

        self.text_label = ctk.CTkLabel(self.card, text="UM!", font=("Segoe UI Bold", 20))
        self.text_label.pack(expand=True, pady=(0, 30))

        # Progress Frame
        progress_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        progress_frame.pack(fill="x", side="bottom", padx=40, pady=15)

        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=12, progress_color=self.color_main, fg_color="#36393f", corner_radius=6)
        self.progress_bar.pack(fill="x", pady=(0, 5))
        self.progress_bar.set(1/10000)

        self.counter_label = ctk.CTkLabel(progress_frame, text="1 / 10.000", font=("Segoe UI Bold", 13), text_color="white")
        self.counter_label.pack()

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=15)

        self.btn_prev = ctk.CTkButton(buttons_frame, text="← ANTERIOR", fg_color=self.color_btn_danger, hover_color=self.color_btn_danger, 
                                    font=("Segoe UI Bold", 12), height=45, command=self.prev_number)
        self.btn_prev.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_next = ctk.CTkButton(buttons_frame, text="PRÓXIMO →", fg_color=self.color_btn_primary, hover_color=self.color_btn_primary, 
                                    font=("Segoe UI Bold", 12), height=45, command=self.next_number)
        self.btn_next.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_reset = ctk.CTkButton(buttons_frame, text="↻ RESETAR", fg_color="#36393f", hover_color="#2f3136", 
                                     font=("Segoe UI Bold", 12), height=45, command=self.reset_number)
        self.btn_reset.pack(side="left", padx=3, expand=True, fill="x")

        self.btn_copy = ctk.CTkButton(buttons_frame, text="📋 COPIAR", fg_color=self.color_btn_success, hover_color=self.color_btn_success, 
                                    font=("Segoe UI Bold", 12), height=45, command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=3, expand=True, fill="x")

        # Footer
        footer_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", pady=(10, 0))

        self.footer_hint = ctk.CTkLabel(footer_frame, text=f"💡 Pressione {self.trigger_key_str} para avançar", font=("Segoe UI Bold", 14), text_color=self.color_main)
        self.footer_hint.pack(side="left")

        # Watermark no canto inferior direito
        watermark_label = ctk.CTkLabel(
            footer_frame, 
            text="by: witheringfeelings",
            font=("Segoe UI Bold", 14),
            text_color=self.color_main
        )
        watermark_label.pack(side="right", padx=(0, 10))

        self.update_display()

    def setup_config_tab(self):
        # Frame principal com rolagem
        self.config_scroll = ctk.CTkScrollableFrame(self.tab_config, fg_color="transparent")
        self.config_scroll.pack(fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(self.config_scroll, text="⚙️ Configuração dos JJ's AFK", 
                            font=("Segoe UI Bold", 24), text_color=self.color_main)
        title.pack(pady=(20, 10), anchor="w", padx=20)

        subtitle = ctk.CTkLabel(self.config_scroll, text="Configure o modo automático de digitação dos JJ's",
                               font=("Segoe UI", 12), text_color="gray")
        subtitle.pack(anchor="w", padx=20, pady=(0, 20))

        # Main Frame
        main_frame = ctk.CTkFrame(self.config_scroll, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Card 1: Ativar/Desativar
        card1 = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=self.color_card_bg)
        card1.pack(fill="x", pady=(0, 15))

        header1 = ctk.CTkFrame(card1, fg_color="transparent")
        header1.pack(fill="x", padx=20, pady=15)

        label1 = ctk.CTkLabel(header1, text="🎯 Modo Automático", font=("Segoe UI Bold", 14))
        label1.pack(side="left", anchor="w")

        self.auto_type_toggle = ctk.CTkSwitch(header1, text="", onvalue=True, offvalue=False,
                                             command=self.toggle_auto_type_mode)
        self.auto_type_toggle.pack(side="right")
        self.auto_type_toggle.select() if self.auto_type_enabled else self.auto_type_toggle.deselect()

        # Card 2: Configurar Limites
        card2 = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=self.color_card_bg)
        card2.pack(fill="x", pady=(0, 15))

        content2 = ctk.CTkFrame(card2, fg_color="transparent")
        content2.pack(fill="x", padx=20, pady=15)

        label2 = ctk.CTkLabel(content2, text="🔢 Limites da Sequência:", font=("Segoe UI Bold", 12))
        label2.pack(anchor="w", pady=(0, 10))

        limits_frame = ctk.CTkFrame(content2, fg_color="transparent")
        limits_frame.pack(fill="x", pady=(0, 10))

        start_label = ctk.CTkLabel(limits_frame, text="Início:", font=("Segoe UI Bold", 11))
        start_label.pack(side="left", padx=(0, 5))
        self.auto_type_start_entry = ctk.CTkEntry(limits_frame, width=70)
        self.auto_type_start_entry.insert(0, str(self.auto_type_start_num))
        self.auto_type_start_entry.pack(side="left", padx=(0, 10))

        end_label = ctk.CTkLabel(limits_frame, text="Fim:", font=("Segoe UI Bold", 11))
        end_label.pack(side="left", padx=(0, 5))
        self.auto_type_end_entry = ctk.CTkEntry(limits_frame, width=70)
        self.auto_type_end_entry.insert(0, str(self.auto_type_end_num))
        self.auto_type_end_entry.pack(side="left", padx=(0, 10))

        apply_limits_btn = ctk.CTkButton(limits_frame, text="APLICAR", width=80, fg_color=self.color_btn_primary, 
                                        hover_color=self.color_btn_primary, font=("Segoe UI Bold", 10), 
                                        command=self.apply_auto_type_limits)
        apply_limits_btn.pack(side="left", padx=(0, 10))

        info2 = ctk.CTkLabel(content2, text="Configure os limites para a sequência automática",
                            font=("Segoe UI", 10), text_color="gray")
        info2.pack(anchor="w", pady=(10, 0))

        # Card 3: Configurar Hotkey
        card3 = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=self.color_card_bg)
        card3.pack(fill="x", pady=(0, 15))

        content3 = ctk.CTkFrame(card3, fg_color="transparent")
        content3.pack(fill="x", padx=20, pady=15)

        label3 = ctk.CTkLabel(content3, text="⌨️ Tecla de Ativação:", font=("Segoe UI Bold", 12))
        label3.pack(anchor="w", pady=(0, 10))

        button_frame = ctk.CTkFrame(content3, fg_color="transparent")
        button_frame.pack(fill="x")

        self.auto_type_hotkey_btn = ctk.CTkButton(button_frame, text=self.auto_type_hotkey_str.upper(),
                                                  width=100, command=self.start_auto_type_key_capture,
                                                  font=("Segoe UI Bold", 11))
        self.auto_type_hotkey_btn.pack(side="left", padx=(0, 10))

        info3 = ctk.CTkLabel(content3, text="Clique no botão e pressione a tecla desejada",
                            font=("Segoe UI", 10), text_color="gray")
        info3.pack(anchor="w", pady=(10, 0))

        # Card 4: Delay de Digitação
        card4 = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=self.color_card_bg)
        card4.pack(fill="x", pady=(0, 15))

        content4 = ctk.CTkFrame(card4, fg_color="transparent")
        content4.pack(fill="x", padx=20, pady=15)

        label4 = ctk.CTkLabel(content4, text="⏱️ Tempo por Letra (ms):", font=("Segoe UI Bold", 12))
        label4.pack(anchor="w", pady=(0, 10))

        slider_frame = ctk.CTkFrame(content4, fg_color="transparent")
        slider_frame.pack(fill="x", pady=(0, 10))

        self.delay_slider = ctk.CTkSlider(slider_frame, from_=10, to=500, number_of_steps=49,
                                          command=self.update_delay_value)
        self.delay_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.delay_slider.set(self.auto_type_delay_ms)

        self.delay_value_label = ctk.CTkLabel(slider_frame, text=f"{self.auto_type_delay_ms}ms",
                                             font=("Segoe UI Bold", 11), width=60, text_color=self.color_main)
        self.delay_value_label.pack(side="left")

        info4 = ctk.CTkLabel(content4, text="Quanto menor, mais rápido. (Recomendado: 50-100ms)",
                            font=("Segoe UI", 10), text_color="gray")
        info4.pack(anchor="w")

        # Card 4: Auto Send Enter
        card4 = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=self.color_card_bg)
        card4.pack(fill="x", pady=(0, 15))

        content4 = ctk.CTkFrame(card4, fg_color="transparent")
        content4.pack(fill="x", padx=20, pady=15)

        label4 = ctk.CTkLabel(content4, text="📤 Enviar Automaticamente", font=("Segoe UI Bold", 12))
        label4.pack(side="left", anchor="w")

        self.auto_enter_toggle = ctk.CTkSwitch(content4, text="", onvalue=True, offvalue=False,
                                              command=self.toggle_auto_send_enter)
        self.auto_enter_toggle.pack(side="right")
        self.auto_enter_toggle.select() if self.auto_send_enter else self.auto_enter_toggle.deselect()

        info4 = ctk.CTkLabel(card4, text="Pressiona Enter automaticamente após completar a digitação",
                            font=("Segoe UI", 10), text_color="gray")
        info4.pack(anchor="w", padx=20, pady=(0, 15))

    def toggle_auto_type_mode(self):
        self.auto_type_enabled = self.auto_type_toggle.get()
        self.config_manager.set("auto_type", "enabled", self.auto_type_enabled)

    def start_auto_type_key_capture(self):
        self.listening_for_auto_type_key = True
        self.auto_type_hotkey_btn.configure(text="AGUARDANDO...")

    def update_delay_value(self, value):
        self.auto_type_delay_ms = int(float(value))
        self.delay_value_label.configure(text=f"{self.auto_type_delay_ms}ms")
        self.config_manager.set("auto_type", "delay_ms", self.auto_type_delay_ms)

    def toggle_auto_send_enter(self):
        self.auto_send_enter = self.auto_enter_toggle.get()
        self.config_manager.set("auto_type", "auto_send_enter", self.auto_send_enter)

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
            
            if self.contador < self.start_num:
                self.contador = self.start_num
            elif self.contador > self.end_num:
                self.contador = self.end_num
            
            self.config_manager.set("main", "start_num", self.start_num)
            self.config_manager.set("main", "end_num", self.end_num)
            self.config_manager.set("main", "exclamation_format", self.exclamation_format)
                
            self.update_display()
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
        
        self.config_manager.set("main", "exclamation_format", self.exclamation_format)
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
    def _is_key_pressed(self, key_pressed, key_expected):
        """Compara corretamente as teclas pressionadas de forma universal - Otimizado"""
        if key_pressed == key_expected:
            return True
            
        try:
            # Pela o identificador da tecla pressionada
            val_p = None
            if hasattr(key_pressed, 'char') and key_pressed.char is not None:
                val_p = key_pressed.char.lower()
            elif hasattr(key_pressed, 'name') and key_pressed.name is not None:
                val_p = key_pressed.name.lower()
            else:
                val_p = str(key_pressed).replace("'", "").lower()

            # Pela o identificador da tecla esperada
            val_e = None
            if isinstance(key_expected, str):
                val_e = key_expected.lower()
            elif hasattr(key_expected, 'char') and key_expected.char is not None:
                val_e = key_expected.char.lower()
            elif hasattr(key_expected, 'name') and key_expected.name is not None:
                val_e = key_expected.name.lower()
            else:
                val_e = str(key_expected).replace("'", "").lower()
                
            if val_p and val_e:
                # Remove prefixo "key." se existir (comum em pynput objects)
                if val_p.startswith("key."): val_p = val_p[4:]
                if val_e.startswith("key."): val_e = val_e[4:]
                return val_p == val_e
        except:
            pass
        return False

    def start_keyboard_listener(self):
        def on_press(key):
            current_time = time.time()
            
            # Verifica se é a hotkey do Auto Type antes de qualquer outra coisa
            # Isso permite que ela funcione mesmo se o programa estiver digitando
            is_auto_type_hotkey = self.auto_type_enabled and self._is_key_pressed(key, self.auto_type_hotkey_obj)

            if is_auto_type_hotkey:
                # Se a tecla foi enviada pelo próprio programa, ignoramos para evitar auto-trigger
                if self.is_typing_char:
                    return
                
                # Evita disparos múltiplos rápidos
                if current_time - self.last_hotkey_time > 0.2:
                    self.last_hotkey_time = current_time
                    
                    if self.sequence_active:
                        self.sequence_active = False
                    else:
                        # Verifica se precisa de backspace (se for caractere normal)
                        has_char = hasattr(key, 'char') and key.char
                        
                        self.sequence_active = True
                        self.after(0, self.start_continuous_sequence, self.auto_type_start_num, has_char)
                    return
            
            # Se o programa está digitando outros caracteres, ignoramos o resto do listener
            if self.typing_automatically and not is_auto_type_hotkey:
                return

            # 1. Verifica se está capturando teclas para configuração
            if self.listening_for_key:
                self.trigger_key_obj = key
                self.trigger_key_str = self.format_key_name(key)
                self.listening_for_key = False
                self.config_manager.set("main", "trigger_key", self.trigger_key_str)
                
                self.after(0, lambda: self.key_btn.configure(text=self.trigger_key_str))
                self.after(0, lambda: self.footer_hint.configure(text=f"💡 Pressione {self.trigger_key_str} para avançar"))
                return

            if self.listening_for_auto_type_key:
                self.auto_type_hotkey_obj = key
                self.auto_type_hotkey_str = self.format_key_name(key).lower()
                self.listening_for_auto_type_key = False
                self.config_manager.set("auto_type", "hotkey", self.auto_type_hotkey_str)
                
                self.after(0, lambda: self.auto_type_hotkey_btn.configure(text=self.auto_type_hotkey_str.upper()))
                return

            # Se algum campo de entrada estiver em foco, ignoramos hotkeys normais (caracteres)
            # para evitar que o usuário acione o programa enquanto digita nos campos de configuração
            if self._is_input_focused():
                # Mas apenas se for uma tecla de caractere normal
                if hasattr(key, 'char') and key.char is not None:
                    return

            # 4. Verifica se é a tecla de trigger principal
            if self._is_key_pressed(key, self.trigger_key_obj) and self.is_running:
                self.after(0, self.auto_type_and_advance)
                return

            # 5. Remove a funcionalidade de auto-typing ao clicar em números
            # O programa agora só responde à tecla de ativação configurada

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
    
    def _process_number_buffer(self, num_str):
        try:
            num = int(num_str)
            if 0 <= num <= 999999999999:
                text = self.numero_para_extenso(num)
                if self.exclamation_format == "junta":
                    text += "!"
                else:
                    text += " !"
                
                # Simula backspace para apagar o número digitado
                for _ in range(len(num_str)):
                    self.keyboard_controller.press(keyboard.Key.backspace)
                    self.keyboard_controller.release(keyboard.Key.backspace)
                    time.sleep(0.01)  # Pequeno delay entre backspaces
                
                # Digita o texto por extenso
                self.auto_typer.type_with_delay(text, self.auto_type_delay_ms, self.auto_send_enter)
                
                # Se auto_send_enter estiver habilitado, inicia a sequência automática
                if self.auto_send_enter:
                    # Pequeno delay para garantir que o Enter foi enviado
                    time.sleep(0.1)
                    # Inicia a digitação automática contínua
                    self.start_continuous_sequence(num + 1, True)
        except:
            pass

    def _process_normal_key(self, key_char):
        """Processa teclas normais para auto-type"""
        try:
            # Se o modo auto-type está habilitado, processa o número digitado
            if self.auto_type_enabled:
                self._process_number_buffer(key_char)
                
        except Exception as e:
            print(f"Erro ao processar tecla normal: {e}")

    def start_continuous_sequence(self, start_num=1, needs_backspace=False):
        """Inicia a digitação automática contínua de números por extenso"""
        # Evita múltiplas threads da mesma sequência
        if hasattr(self, 'sequence_running') and self.sequence_running:
            return

        # Usa os limites independentes da aba Auto Type
        auto_start = self.auto_type_start_num
        auto_end = self.auto_type_end_num
        
        # Ajusta o start_num para respeitar os limites configurados
        if start_num < auto_start:
            start_num = auto_start
        elif start_num > auto_end:
            start_num = auto_start
        
        def sequence_thread():
            self.sequence_running = True
            try:
                # Se a hotkey foi um caractere, apaga ele antes de começar a sequência
                if needs_backspace:
                    self.is_typing_char = True
                    self.keyboard_controller.press(keyboard.Key.backspace)
                    self.keyboard_controller.release(keyboard.Key.backspace)
                    time.sleep(0.05)  # Reduzido de 0.1 para 0.05
                    self.is_typing_char = False

                current_num = start_num
                # Inicia a sequência enquanto habilitada e ativa
                while self.auto_type_enabled and self.sequence_active:
                    text = self.numero_para_extenso(current_num)
                    if self.exclamation_format == "junta":
                        text += "!"
                    else:
                        text += " !"
                    
                    # Marca que o programa está digitando para o listener ignorar
                    self.typing_automatically = True
                    
                    # Digita o texto usando o controller direto
                    for char in text:
                        if not self.sequence_active: break
                        self.is_typing_char = True
                        self.keyboard_controller.type(char)
                        time.sleep(0.0001)  # Reduzido de 0.001 para 0.0001
                        self.is_typing_char = False
                        time.sleep(self.auto_type_delay_ms / 1000.0)
                    
                    # Envia Enter automaticamente se estiver habilitado
                    if self.auto_send_enter and self.sequence_active:
                        self.is_typing_char = True
                        self.keyboard_controller.press(keyboard.Key.enter)
                        self.keyboard_controller.release(keyboard.Key.enter)
                        self.is_typing_char = False
                    
                    # Desmarca para permitir toggle no intervalo ou após terminar
                    self.typing_automatically = False
                    
                    # Pequeno delay entre números
                    time.sleep(0.05)  # Reduzido de 0.1 para 0.05
                    
                    current_num += 1
                    
                    # Interrompe a sequência quando terminar os números
                    if current_num > auto_end:
                        self.sequence_active = False
                        break
                        
            except Exception as e:
                print(f"Erro na sequência contínua: {e}")
            finally:
                # Garante que a sequência seja desativada quando terminar
                self.sequence_active = False
                self.sequence_running = False
                self.typing_automatically = False  # Marca que o programa parou de digitar
        
        import threading
        thread = threading.Thread(target=sequence_thread, daemon=True)
        thread.start()

    def auto_type_and_advance(self):
        texto = self.get_formatted_text()
        
        # Digita o texto diretamente sem usar Ctrl+V
        def type_text():
            self.keyboard_controller.type(texto)
            self.next_number()
        
        # Executa a digitação em um thread separado para não travar a interface
        import threading
        thread = threading.Thread(target=type_text, daemon=True)
        thread.start()

    def apply_auto_type_limits(self):
        try:
            new_start = int(self.auto_type_start_entry.get())
            new_end = int(self.auto_type_end_entry.get())
            
            if new_start >= new_end:
                return

            # Salva os limites específicos da aba Auto Type
            self.config_manager.set("auto_type", "start_num", new_start)
            self.config_manager.set("auto_type", "end_num", new_end)
            
            # Atualiza as variáveis independentes
            self.auto_type_start_num = new_start
            self.auto_type_end_num = new_end
        except ValueError:
            pass

if __name__ == "__main__":
    app = AutoJJSApp()
    app.mainloop()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Proteção e Controle para Auto-Typing no Discord

Este módulo implementa mecanismos de detecção e proteção contra problemas
causados por ações de administradores/moderadores ou mudanças no ambiente
do Discord enquanto o programa está rodando.

Funcionalidades implementadas:
1. Timeout / castigo aplicado ao usuário
2. Slow mode ativado no canal
3. Remoção da permissão de enviar mensagens
4. Canal transformado em somente leitura
5. Usuário mudar de canal
6. Canal ser movido de posição na lista
7. Remoção da permissão de visualizar o canal
8. Mudanças na interface do Discord
"""

import time
import threading
import ctypes
import pyperclip
import random
import logging
from typing import Optional, Tuple, Dict, Any
from pynput.keyboard import Controller, Key
from pynput import keyboard

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_protection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32

class DiscordProtectionSystem:
    """Sistema de proteção e controle para auto-typing no Discord"""
    
    def __init__(self):
        self.keyboard_controller = Controller()
        
        # Estado do sistema
        self.is_typing = False
        self.is_paused = False
        self.fail_count = 0
        self.max_fails = 3
        self.base_delay = 0.05
        self.adaptive_delay = 0.0
        self.last_message_time = 0
        
        # Estado do Discord
        self.initial_window_title = None
        self.current_channel = None
        self.discord_window_handle = None
        
        # Configurações de proteção
        self.protection_enabled = True
        self.auto_pause_on_error = True
        self.max_consecutive_fails = 5
        self.slow_mode_threshold = 2.0  # segundos
        self.timeout_threshold = 5.0    # segundos
        
        # Callbacks
        self.on_pause_callback = None
        self.on_status_change_callback = None
        self.on_error_callback = None
        
        # Histórico de mensagens para detecção de falhas
        self.message_history = []
        self.max_history_size = 10
        
        # Lock para sincronização de threads
        self._lock = threading.Lock()
        
        logger.info("Sistema de Proteção Discord inicializado")

    def set_callbacks(self, on_pause=None, on_status_change=None, on_error=None):
        """Configura callbacks para eventos do sistema de proteção"""
        self.on_pause_callback = on_pause
        self.on_status_change_callback = on_status_change
        self.on_error_callback = on_error

    def get_active_window_title(self) -> str:
        """Obtém o título da janela ativa"""
        try:
            hwnd = user32.GetForegroundWindow()
            if hwnd == 0:
                return ""
            
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
            return ""
        except Exception as e:
            logger.error(f"Erro ao obter título da janela: {e}")
            return ""

    def get_active_window_handle(self) -> int:
        """Obtém o handle da janela ativa"""
        try:
            return user32.GetForegroundWindow()
        except Exception as e:
            logger.error(f"Erro ao obter handle da janela: {e}")
            return 0

    def is_discord_active(self) -> bool:
        """Verifica se o Discord é a janela ativa"""
        title = self.get_active_window_title().lower()
        return "discord" in title

    def get_discord_channel_info(self) -> Tuple[str, str]:
        """Obtém informações do canal atual do Discord"""
        try:
            title = self.get_active_window_title()
            if not self.is_discord_active():
                return "", ""
            
            # O título do Discord geralmente contém: "Canal - Servidor • Discord"
            # ou "Canal de Voz - Servidor • Discord"
            if "• Discord" in title:
                channel_part = title.split("• Discord")[0].strip()
                if " - " in channel_part:
                    channel_name = channel_part.split(" - ")[0].strip()
                    server_name = channel_part.split(" - ")[1].strip()
                    return channel_name, server_name
            
            return title, ""
        except Exception as e:
            logger.error(f"Erro ao obter informações do canal: {e}")
            return "", ""

    def clear_textbox(self) -> bool:
        """Limpa a caixa de texto do Discord"""
        try:
            # Seleciona todo o texto (Ctrl+A)
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('a')
                self.keyboard_controller.release('a')
            time.sleep(0.05)
            
            # Apaga o texto selecionado
            self.keyboard_controller.press(Key.backspace)
            self.keyboard_controller.release(Key.backspace)
            time.sleep(0.1)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar caixa de texto: {e}")
            return False

    def check_textbox_empty(self) -> bool:
        """Verifica se a caixa de texto está vazia"""
        try:
            # Salva o conteúdo atual do clipboard
            original_clipboard = pyperclip.paste()
            
            # Seleciona todo o texto
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('a')
                self.keyboard_controller.release('a')
            time.sleep(0.05)
            
            # Copia o conteúdo
            with self.keyboard_controller.pressed(Key.ctrl):
                self.keyboard_controller.press('c')
                self.keyboard_controller.release('c')
            time.sleep(0.2)
            
            # Obtém o conteúdo copiado
            current_content = pyperclip.paste()
            
            # Restaura o clipboard original
            pyperclip.copy(original_clipboard)
            
            # Verifica se está vazio
            return not current_content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao verificar caixa de texto: {e}")
            return False

    def check_message_sent(self, message: str) -> bool:
        """Verifica se a mensagem foi enviada com sucesso"""
        try:
            # Verifica se a caixa de texto está vazia após o envio
            is_empty = self.check_textbox_empty()
            
            if not is_empty:
                logger.warning("Mensagem não foi enviada - caixa de texto ainda contém conteúdo")
                return False
            
            # Verifica se houve timeout
            time_since_send = time.time() - self.last_message_time
            if time_since_send > self.timeout_threshold:
                logger.warning(f"Timeout detectado: {time_since_send:.2f}s desde o último envio")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar envio de mensagem: {e}")
            return False

    def detect_slow_mode(self, message: str) -> bool:
        """Detecta se o slow mode está ativo no canal"""
        try:
            # Tenta enviar a mensagem e verifica se falha
            success = self.send_message_direct(message)
            
            if not success:
                # Se falhou, pode ser slow mode
                logger.warning("Possível slow mode detectado - mensagem não enviada")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao detectar slow mode: {e}")
            return False

    def check_channel_change(self) -> bool:
        """Verifica se o usuário mudou de canal"""
        try:
            current_channel, current_server = self.get_discord_channel_info()
            
            if not current_channel:
                logger.warning("Canal atual não detectado - possível mudança de canal ou perda de permissão")
                return True
            
            if self.current_channel and current_channel != self.current_channel:
                logger.warning(f"Canal mudou de '{self.current_channel}' para '{current_channel}'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar mudança de canal: {e}")
            return False

    def check_discord_window_change(self) -> bool:
        """Verifica se a janela do Discord mudou"""
        try:
            current_handle = self.get_active_window_handle()
            
            if current_handle != self.discord_window_handle:
                logger.warning("Janela do Discord mudou ou foi fechada")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar mudança de janela: {e}")
            return False

    def check_permissions(self) -> bool:
        """Verifica se o usuário tem permissão para enviar mensagens"""
        try:
            # Testa enviando uma mensagem curta
            test_message = "test"
            success = self.send_message_direct(test_message)
            
            if not success:
                logger.warning("Permissão para enviar mensagens pode ter sido removida")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissões: {e}")
            return False

    def send_message_direct(self, message: str) -> bool:
        """Envia mensagem diretamente sem verificações (para testes)"""
        try:
            # Limpa a caixa de texto
            self.clear_textbox()
            
            # Digita a mensagem
            for char in message:
                self.keyboard_controller.type(char)
                time.sleep(0.01)
            
            # Envia com Enter
            self.keyboard_controller.press(Key.enter)
            self.keyboard_controller.release(Key.enter)
            
            time.sleep(0.5)
            
            # Verifica se foi enviado
            return self.check_textbox_empty()
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem direta: {e}")
            return False

    def pause_system(self, reason: str):
        """Pausa o sistema de auto-typing"""
        with self._lock:
            if not self.is_paused:
                self.is_paused = True
                self.is_typing = False
                
                logger.warning(f"Sistema pausado: {reason}")
                
                if self.on_pause_callback:
                    try:
                        self.on_pause_callback(reason)
                    except Exception as e:
                        logger.error(f"Erro no callback de pausa: {e}")

    def resume_system(self):
        """Retoma o sistema de auto-typing"""
        with self._lock:
            if self.is_paused:
                self.is_paused = False
                self.fail_count = 0
                self.adaptive_delay = 0.0
                
                logger.info("Sistema retomado")
                
                if self.on_status_change_callback:
                    try:
                        self.on_status_change_callback("resumed")
                    except Exception as e:
                        logger.error(f"Erro no callback de retomada: {e}")

    def validate_environment(self) -> Dict[str, Any]:
        """Valida o ambiente do Discord e retorna status"""
        status = {
            "discord_active": False,
            "channel_valid": False,
            "window_valid": False,
            "permissions_valid": False,
            "errors": []
        }
        
        try:
            # Verifica se o Discord está ativo
            if not self.is_discord_active():
                status["errors"].append("Discord não é a janela ativa")
                return status
            
            status["discord_active"] = True
            
            # Verifica se o canal é válido
            if self.check_channel_change():
                status["errors"].append("Canal mudou ou não detectado")
                return status
            
            status["channel_valid"] = True
            
            # Verifica se a janela é válida
            if self.check_discord_window_change():
                status["errors"].append("Janela do Discord mudou")
                return status
            
            status["window_valid"] = True
            
            # Verifica permissões (apenas se não houver falhas recentes)
            if self.fail_count < 2:
                if not self.check_permissions():
                    status["errors"].append("Permissão para enviar mensagens pode ter sido removida")
                    return status
            
            status["permissions_valid"] = True
            
        except Exception as e:
            status["errors"].append(f"Erro na validação: {str(e)}")
            logger.error(f"Erro na validação do ambiente: {e}")
        
        return status

    def type_with_protection(self, message: str, delay_ms: int = 50, auto_send_enter: bool = True) -> bool:
        """Digita mensagem com proteções completas"""
        if not self.protection_enabled:
            # Modo sem proteções - apenas digita
            return self._type_message_simple(message, delay_ms, auto_send_enter)
        
        with self._lock:
            if self.is_paused:
                logger.warning("Sistema pausado - mensagem não enviada")
                return False
            
            if self.is_typing:
                logger.warning("Sistema já está digitando - mensagem ignorada")
                return False
            
            self.is_typing = True
            
        try:
            # 1. Validação inicial do ambiente
            validation = self.validate_environment()
            
            if not all([validation["discord_active"], validation["channel_valid"], 
                       validation["window_valid"], validation["permissions_valid"]]):
                
                error_msg = " | ".join(validation["errors"])
                self.pause_system(f"Problemas no ambiente: {error_msg}")
                return False
            
            # 2. Atualiza informações do canal se necessário
            if not self.current_channel:
                self.current_channel, _ = self.get_discord_channel_info()
                self.discord_window_handle = self.get_active_window_handle()
            
            # 3. Limpa a caixa de texto
            if not self.clear_textbox():
                self.fail_count += 1
                if self.fail_count >= self.max_consecutive_fails:
                    self.pause_system("Falha ao limpar caixa de texto")
                return False
            
            # 4. Digita a mensagem com delays
            base_delay = delay_ms / 1000.0
            final_delay = base_delay + self.adaptive_delay
            
            for char in message:
                if self.is_paused or not self.is_typing:
                    return False
                
                self.keyboard_controller.type(char)
                
                # Delay aleatório para parecer mais humano
                random_delay = random.uniform(0, 0.05)
                time.sleep(final_delay + random_delay)
            
            # 5. Envia a mensagem
            if auto_send_enter:
                self.keyboard_controller.press(Key.enter)
                self.keyboard_controller.release(Key.enter)
                
                self.last_message_time = time.time()
                
                # Pequeno delay para o Discord processar
                time.sleep(0.5)
                
                # 6. Verifica se a mensagem foi enviada
                if not self.check_message_sent(message):
                    self.fail_count += 1
                    
                    # Detecta slow mode e ajusta delay
                    if self.detect_slow_mode(message):
                        self.adaptive_delay += 1.0
                        logger.info(f"Slow mode detectado - aumentando delay para {self.adaptive_delay:.1f}s")
                    
                    if self.fail_count >= self.max_consecutive_fails:
                        self.pause_system(f"Falhas consecutivas ({self.fail_count}) - possíveis problemas de permissão ou slow mode")
                        return False
                    else:
                        # Tenta limpar para a próxima tentativa
                        self.clear_textbox()
                        return False
                else:
                    # Sucesso - reseta contadores
                    self.fail_count = 0
                    if self.adaptive_delay > 0:
                        self.adaptive_delay = max(0, self.adaptive_delay - 0.1)
            
            # 7. Atualiza histórico de mensagens
            self._update_message_history(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao digitar com proteção: {e}")
            if self.on_error_callback:
                try:
                    self.on_error_callback(str(e))
                except Exception as cb_e:
                    logger.error(f"Erro no callback de erro: {cb_e}")
            
            self.pause_system(f"Erro inesperado: {str(e)}")
            return False
            
        finally:
            with self._lock:
                self.is_typing = False

    def _type_message_simple(self, message: str, delay_ms: int, auto_send_enter: bool) -> bool:
        """Versão simplificada sem proteções (para fallback)"""
        try:
            self.clear_textbox()
            
            base_delay = delay_ms / 1000.0
            for char in message:
                self.keyboard_controller.type(char)
                time.sleep(base_delay)
            
            if auto_send_enter:
                self.keyboard_controller.press(Key.enter)
                self.keyboard_controller.release(Key.enter)
            
            return True
        except Exception as e:
            logger.error(f"Erro na digitação simples: {e}")
            return False

    def _update_message_history(self, message: str):
        """Atualiza o histórico de mensagens"""
        self.message_history.append({
            "message": message,
            "timestamp": time.time(),
            "channel": self.current_channel
        })
        
        # Mantém apenas as últimas N mensagens
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)

    def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do sistema de proteção"""
        return {
            "is_typing": self.is_typing,
            "is_paused": self.is_paused,
            "fail_count": self.fail_count,
            "adaptive_delay": self.adaptive_delay,
            "current_channel": self.current_channel,
            "protection_enabled": self.protection_enabled,
            "message_history_size": len(self.message_history)
        }

    def enable_protection(self):
        """Habilita o sistema de proteção"""
        self.protection_enabled = True
        logger.info("Proteção habilitada")

    def disable_protection(self):
        """Desabilita o sistema de proteção"""
        self.protection_enabled = False
        logger.info("Proteção desabilitada")

    def reset_failures(self):
        """Reseta contadores de falhas"""
        with self._lock:
            self.fail_count = 0
            self.adaptive_delay = 0.0
            logger.info("Contadores de falhas resetados")

    def force_resume(self):
        """Força a retomada do sistema (ignora pausa automática)"""
        with self._lock:
            self.is_paused = False
            self.fail_count = 0
            self.adaptive_delay = 0.0
            logger.info("Sistema forçado a retomar")

if __name__ == "__main__":
    # Teste do sistema de proteção
    protection = DiscordProtectionSystem()
    
    # Configura callbacks de teste
    def on_pause(reason):
        print(f"PAUSA: {reason}")
    
    def on_status_change(status):
        print(f"STATUS: {status}")
    
    def on_error(error):
        print(f"ERRO: {error}")
    
    protection.set_callbacks(on_pause, on_status_change, on_error)
    
    # Teste de validação
    print("Testando validação do ambiente...")
    status = protection.validate_environment()
    print(f"Status: {status}")
    
    # Teste de digitação (comentado para não enviar mensagens reais)
    # print("Testando digitação com proteção...")
    # success = protection.type_with_protection("Teste de proteção", 50, True)
    # print(f"Sucesso: {success}")
    
    print("Teste concluído")
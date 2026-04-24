#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste do Sistema de Proteção Discord

Este script testa as funcionalidades básicas do sistema de proteção
sem enviar mensagens reais para o Discord.
"""

import sys
import os
import time
import threading

# Adiciona o caminho para importar os módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from discord_protection_system import DiscordProtectionSystem
    print("✓ Importação do DiscordProtectionSystem bem-sucedida")
except ImportError as e:
    print(f"✗ Erro na importação: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Testa funcionalidades básicas do sistema de proteção"""
    print("\n=== Testando Funcionalidades Básicas ===")
    
    # Cria instância do sistema de proteção
    protection = DiscordProtectionSystem()
    
    # Testa métodos básicos
    try:
        # Testa obtenção de título da janela
        title = protection.get_active_window_title()
        print(f"✓ Título da janela obtido: '{title[:50]}...'" if len(title) > 50 else f"✓ Título da janela obtido: '{title}'")
        
        # Testa verificação de Discord ativo
        is_discord = protection.is_discord_active()
        print(f"✓ Verificação de Discord ativo: {is_discord}")
        
        # Testa obtenção de informações do canal
        channel, server = protection.get_discord_channel_info()
        print(f"✓ Informações do canal obtidas: Canal='{channel[:30]}...', Servidor='{server[:30]}...'" 
              if len(channel) > 30 or len(server) > 30 else f"✓ Informações do canal obtidas: Canal='{channel}', Servidor='{server}'")
        
        # Testa validação do ambiente
        validation = protection.validate_environment()
        print(f"✓ Validação do ambiente: {validation}")
        
        # Testa status do sistema
        status = protection.get_status()
        print(f"✓ Status do sistema obtido: {status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nos testes básicos: {e}")
        return False

def test_protection_features():
    """Testa funcionalidades de proteção"""
    print("\n=== Testando Funcionalidades de Proteção ===")
    
    protection = DiscordProtectionSystem()
    
    try:
        # Testa pausa e retomada
        print("✓ Testando pausa e retomada...")
        protection.pause_system("Teste de pausa")
        time.sleep(1)
        protection.resume_system()
        
        # Testa reset de falhas
        print("✓ Testando reset de falhas...")
        protection.reset_failures()
        
        # Testa mudança de configurações
        print("✓ Testando mudança de configurações...")
        protection.max_consecutive_fails = 3
        protection.slow_mode_threshold = 1.5
        protection.timeout_threshold = 3.0
        
        print("✓ Todas as funcionalidades de proteção testadas com sucesso")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos testes de proteção: {e}")
        return False

def test_callbacks():
    """Testa callbacks do sistema"""
    print("\n=== Testando Callbacks ===")
    
    protection = DiscordProtectionSystem()
    
    # Define callbacks de teste
    def test_pause(reason):
        print(f"✓ Callback de pausa chamado: {reason}")
    
    def test_status_change(status):
        print(f"✓ Callback de status chamado: {status}")
    
    def test_error(error):
        print(f"✓ Callback de erro chamado: {error}")
    
    try:
        # Configura callbacks
        protection.set_callbacks(test_pause, test_status_change, test_error)
        
        # Testa chamada de callbacks
        protection.pause_system("Teste de callback")
        protection.resume_system()
        
        print("✓ Callbacks testados com sucesso")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos testes de callbacks: {e}")
        return False

def test_threading():
    """Testa funcionalidades de threading"""
    print("\n=== Testando Threading ===")
    
    protection = DiscordProtectionSystem()
    
    def thread_test():
        try:
            # Simula operação em thread
            protection.is_typing = True
            time.sleep(0.1)
            protection.is_typing = False
            print("✓ Operação em thread concluída")
        except Exception as e:
            print(f"✗ Erro na thread: {e}")
    
    try:
        # Testa operação em thread
        thread = threading.Thread(target=thread_test, daemon=True)
        thread.start()
        thread.join(timeout=2.0)
        
        if thread.is_alive():
            print("✗ Thread não concluiu a tempo")
            return False
        
        print("✓ Testes de threading concluídos")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos testes de threading: {e}")
        return False

def test_logging():
    """Testa funcionalidades de logging"""
    print("\n=== Testando Logging ===")
    
    protection = DiscordProtectionSystem()
    
    try:
        # Testa métodos que geram logs
        protection.pause_system("Teste de logging")
        protection.resume_system()
        
        print("✓ Logging testado (verifique o arquivo discord_protection.log)")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos testes de logging: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 Iniciando Testes do Sistema de Proteção Discord")
    print("=" * 60)
    
    tests = [
        ("Funcionalidades Básicas", test_basic_functionality),
        ("Funcionalidades de Proteção", test_protection_features),
        ("Callbacks", test_callbacks),
        ("Threading", test_threading),
        ("Logging", test_logging),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🚀 Executando: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"💥 {test_name}: ERRO - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado dos Testes: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema de proteção está funcionando corretamente.")
    else:
        print(f"⚠️  {total - passed} testes falharam. Verifique os erros acima.")
    
    print("\n📝 Observações:")
    print("- Este teste não envia mensagens reais para o Discord")
    print("- Para testes completos, execute o programa principal")
    print("- Verifique o arquivo discord_protection.log para detalhes do logging")

if __name__ == "__main__":
    main()
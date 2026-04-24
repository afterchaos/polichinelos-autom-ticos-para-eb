# Sistema de Proteção e Controle para Auto-Typing no Discord

## Visão Geral

Este documento descreve o sistema de proteção e controle implementado para o programa de auto-typing de JJ's no Discord. O sistema foi projetado para detectar e mitigar problemas causados por ações de administradores/moderadores ou mudanças no ambiente do Discord.

## Arquitetura do Sistema

### Componentes Principais

1. **discord_protection_system.py** - Sistema de proteção avançado
2. **auto_typer.py** - Sistema de digitação com integração de proteção
3. **main.py** - Interface gráfica com controles de proteção

### Estrutura de Classes

#### DiscordProtectionSystem
Classe principal que implementa todas as funcionalidades de proteção:

- **Detecção de Ambiente**: Verifica se o Discord está ativo, canal válido, permissões
- **Proteção contra Falhas**: Controla falhas consecutivas, timeouts, slow mode
- **Gerenciamento de Estado**: Pausa/retoma automática, callbacks de eventos
- **Validação Contínua**: Monitoramento constante do ambiente Discord

#### AutoTyper
Classe de digitação existente com integração do sistema de proteção:

- **Compatibilidade**: Mantém funcionalidades existentes
- **Fallback**: Sistema antigo como backup
- **Integração**: Conecta-se ao DiscordProtectionSystem

## Funcionalidades Implementadas

### 1. Timeout / Castigo Aplicado ao Usuário
- **Detecção**: Verifica se a mensagem não foi enviada após pressionar Enter
- **Prevenção**: Evita acumulação de texto na caixa de mensagem
- **Pausa Automática**: Interrompe o sistema após falhas consecutivas

### 2. Slow Mode Ativado no Canal
- **Detecção**: Identifica slow mode através de falhas de envio
- **Adaptação**: Aumenta automaticamente o tempo de espera entre mensagens
- **Ajuste Dinâmico**: Delay adaptativo baseado na detecção de slow mode

### 3. Remoção da Permissão de Enviar Mensagens
- **Verificação**: Testa permissões enviando mensagem de teste
- **Detecção**: Identifica falhas persistentes como possível remoção de permissão
- **Pausa**: Interrompe temporariamente a execução

### 4. Canal Transformado em Somente Leitura
- **Detecção**: Usa a mesma lógica de falha de envio
- **Prevenção**: Impede digitação indefinida em canal sem permissão

### 5. Usuário Mudar de Canal
- **Monitoramento**: Verifica constantemente o canal atual
- **Detecção**: Compara título da janela antes e depois
- **Pausa**: Interrompe automaticamente quando o canal muda

### 6. Canal Ser Movido de Posição na Lista
- **Independência**: Sistema não depende de coordenadas fixas
- **Foco**: Concentra-se apenas na caixa de mensagem ativa
- **Resiliência**: Não afetado por mudanças na interface visual

### 7. Remoção da Permissão de Visualizar o Canal
- **Detecção**: Identifica quando o canal desaparece ou interface muda
- **Pausa Automática**: Interrompe o script imediatamente

### 8. Mudanças na Interface do Discord
- **Verificação de Foco**: Confirma que o campo de mensagem está ativo
- **Resiliência**: Sistema adaptável a mudanças de layout
- **Proteção**: Evita digitação em campos errados

## Configurações do Sistema

### Proteções Básicas
- **Proteção Habilitada**: Ativa/desativa todo o sistema de proteção
- **Auto Retomada**: Permite retomada automática após pausa (5 segundos)
- **Máximo de Falhas**: Número de falhas consecutivas antes da pausa (padrão: 5)

### Configurações Avançadas
- **Slow Mode Threshold**: Tempo mínimo para detectar slow mode (padrão: 2.0s)
- **Timeout Threshold**: Tempo máximo para detectar timeout (padrão: 5.0s)
- **Delay Adaptativo**: Aumenta automaticamente quando slow mode é detectado

## Uso da Interface

### Aba "⚙️ JJ'S AFK"

#### Sistema de Proteção
- **🛡️ Sistema de Proteção**: Interruptor para habilitar/desabilitar proteções
- **🔄 Auto Retomada**: Permite retomada automática após pausas
- **❌ Máximo de Falhas**: Define limite de falhas antes da pausa
- **🐌 Slow Mode (s)**: Configura tempo para detecção de slow mode
- **⏱️ Timeout (s)**: Configura tempo para detecção de timeout

#### Aplicar Proteções
- Botão para aplicar todas as configurações de proteção
- Validação de valores antes de salvar
- Atualização em tempo real do sistema de proteção

## Integração com o Sistema Externo

### Compatibilidade
- **Sistema Antigo**: Mantém funcionalidades existentes como fallback
- **Modo Simples**: Pode ser desativado para uso sem proteções
- **Performance**: Overhead mínimo quando proteções estão ativas

### Callbacks de Eventos
- **on_pause**: Chamado quando o sistema pausa
- **on_status_change**: Chamado quando o status muda
- **on_error**: Chamado quando ocorre erro

## Logs e Monitoramento

### Logging
- **Arquivo**: discord_protection.log (UTF-8)
- **Console**: Saída padrão para debug
- **Formato**: Timestamp, nível, mensagem

### Mensagens de Status
- **PAUSA AUTOMÁTICA**: Motivo da pausa
- **STATUS PROTEÇÃO**: Mudanças de status
- **ERRO PROTEÇÃO**: Erros no sistema de proteção

## Exemplos de Uso

### Uso Básico
```python
from discord_protection_system import DiscordProtectionSystem

protection = DiscordProtectionSystem()
protection.enable_protection()

# Digita com proteções
success = protection.type_with_protection("UM!", 50, True)
```

### Configuração Personalizada
```python
protection.max_consecutive_fails = 3
protection.slow_mode_threshold = 1.5
protection.timeout_threshold = 3.0
```

### Callbacks Personalizados
```python
def on_pause(reason):
    print(f"Sistema pausado: {reason}")

def on_status_change(status):
    print(f"Status alterado: {status}")

protection.set_callbacks(on_pause, on_status_change, None)
```

## Considerações de Segurança

### Prevenção de Abuso
- **Limites de Taxa**: Evita spam excessivo
- **Validação de Entrada**: Verifica mensagens antes de enviar
- **Timeouts**: Impede bloqueios por espera infinita

### Privacidade
- **Sem Dados Sensíveis**: Não armazena mensagens enviadas
- **Logs Seguros**: Não registra conteúdo das mensagens
- **Memória Temporária**: Histórico limitado e temporário

## Troubleshooting

### Problemas Comuns

#### Sistema Não Detecta Discord
- Verifique se o Discord está aberto e ativo
- Confira se o título da janela contém "Discord"
- Teste a função `is_discord_active()`

#### Mensagens Não São Enviadas
- Verifique permissões no canal
- Confira se slow mode está ativo
- Aumente o delay adaptativo

#### Sistema Pausa Constantemente
- Aumente o número máximo de falhas
- Verifique conexão com Discord
- Confira se o canal é válido

### Debug
```python
# Verifica status do sistema
status = protection.get_status()
print(f"Status: {status}")

# Testa validação do ambiente
validation = protection.validate_environment()
print(f"Validação: {validation}")
```

## Performance

### Otimizações
- **Threading**: Operações em threads separadas
- **Locks**: Sincronização segura entre threads
- **Cache**: Armazenamento temporário de informações

### Recursos
- **CPU**: Uso mínimo (< 1%)
- **Memória**: Consumo baixo (< 10MB)
- **I/O**: Operações rápidas e eficientes

## Futuro Desenvolvimento

### Possíveis Melhorias
- **Detecção Visual**: OCR para confirmar envio de mensagens
- **API Discord**: Integração opcional para melhor detecção
- **Machine Learning**: Aprendizado de padrões de comportamento
- **Multi-Canal**: Suporte a múltiplos canais simultaneamente

### Extensões
- **Plugins**: Sistema de plugins para funcionalidades adicionais
- **Configuração**: Arquivo de configuração avançado
- **Monitoramento**: Dashboard de monitoramento em tempo real

## Licença

Este sistema é parte do projeto AutoJJS e segue os mesmos termos de licenciamento.

## Contribuição

Para contribuir com melhorias no sistema de proteção:

1. Teste as funcionalidades existentes
2. Relate bugs através de issues
3. Proponha melhorias com pull requests
4. Documente novas funcionalidades

---

**Nota**: Este sistema foi projetado para ser robusto e resiliente, mas não pode garantir 100% de proteção contra todas as possíveis mudanças no Discord ou ações de administradores.
from pynput import keyboard
from pynput.keyboard import Controller

# Variável global para manter o continuador
contador = 0

# Dicionários para conversão de números em extenso
unidades = ['', 'UM', 'DOIS', 'TRÊS', 'QUATRO', 'CINCO', 'SEIS', 'SETE', 'OITO', 'NOVE']
dezenas = ['', '', 'VINTE', 'TRINTA', 'QUARENTA', 'CINQUENTA', 'SESSENTA', 'SETENTA', 'OITENTA', 'NOVENTA']
teenagers = ['DEZ', 'ONZE', 'DOZE', 'TREZE', 'QUATORZE', 'QUINZE', 'DEZESSEIS', 'DEZESSETE', 'DEZOITO', 'DEZENOVE']
centenas = ['', 'CENTO', 'DUZENTOS', 'TREZENTOS', 'QUATROCENTOS', 'QUINHENTOS', 'SEISCENTOS', 'SETECENTOS', 'OITOCENTOS', 'NOVECENTOS']
escala = ['', 'MIL', 'MILHÃO', 'BILHÃO']

def converter_grupo(num):
    """Converte um grupo de até 3 dígitos para extenso"""
    if num == 0:
        return ''
    
    resultado = []
    
    # Centenas
    c = num // 100
    if c > 0:
        if c == 1:
            resultado.append('CENTO')
        else:
            resultado.append(centenas[c])
    
    # Dezenas e unidades
    resto = num % 100
    if resto > 0:
        # Adiciona "E" se houver centenas
        if c > 0:
            resultado.append('E')
        
        if 10 <= resto <= 19:
            resultado.append(teenagers[resto - 10])
        else:
            d = resto // 10
            u = resto % 10
            
            if d > 0:
                resultado.append(dezenas[d])
                if u > 0:
                    resultado.append('E')
                    resultado.append(unidades[u])
            elif u > 0:
                resultado.append(unidades[u])
    
    return ' '.join(resultado)

def numero_para_extenso(num):
    """Converte um número (1-10000) para extenso em português"""
    if num == 0:
        return 'ZERO'
    
    if num < 0:
        return 'MENOS ' + numero_para_extenso(-num)
    
    if num < 1 or num > 10000:
        return str(num)
    
    # Processa o número em grupos
    grupos = []
    escala_idx = 0
    
    while num > 0 and escala_idx < len(escala):
        grupo = num % 1000
        
        if grupo != 0:
            texto_grupo = converter_grupo(grupo)
            if escala_idx > 0:
                texto_grupo += ' ' + escala[escala_idx]
            grupos.append(texto_grupo)
        
        num //= 1000
        escala_idx += 1
    
    # Inverte a lista para ordenação correta
    grupos.reverse()
    resultado = ' E '.join(grupos)
    
    # Remove espaços duplicados
    while '  ' in resultado:
        resultado = resultado.replace('  ', ' ')
    
    return resultado.strip()

def on_press(key):
    """Callback quando uma tecla é pressionada"""
    global contador
    try:
        if key == keyboard.Key.tab:
            # Incrementa o contador
            contador += 1
            
            # Se passou de 10000, volta para 1
            if contador > 10000:
                contador = 1
            
            # Converte para extenso
            texto = numero_para_extenso(contador)
            
            # Escreve o texto com exclamação
            controller = Controller()
            controller.type(texto + '!')
            
            print(f"TAB pressionado! Número: {contador} -> {texto}!")
    
    except AttributeError:
        pass

def on_release(key):
    """Callback quando uma tecla é liberada"""
    try:
        if key == keyboard.Key.esc:
            # Pressionar ESC para sair
            return False
    except AttributeError:
        pass

# Configuração do listener
print("Script iniciado!")
print("Pressione TAB para escrever um número por extenso (1-10000)")
print("Pressione ESC para sair\n")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Script encerrado!")

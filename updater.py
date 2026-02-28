import os
import sys
import requests
import subprocess
import tempfile
import time
from packaging.version import parse as parse_version
from tkinter import messagebox, Tk

class Updater:
    def __init__(self, repo_owner, repo_name, current_version, executable_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.executable_name = executable_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def check_for_updates(self):
        """Verifica se há uma nova versão disponível no GitHub Releases."""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            
            latest_version = release_data["tag_name"].lstrip("v")
            
            # Comparação de versão semântica
            if parse_version(latest_version) > parse_version(self.current_version):
                return release_data
            return None
        except Exception as e:
            # Mostra erro apenas se não for timeout (evita incomodar se a net cair)
            if not isinstance(e, requests.exceptions.Timeout):
                print(f"Erro ao verificar atualizações: {e}")
            return None

    def download_and_install(self, release_data):
        """Baixa o novo executável e inicia o processo de substituição."""
        try:
            # Encontrar o asset que é um .exe
            assets = release_data.get("assets", [])
            download_url = None
            asset_name = ""
            for asset in assets:
                if asset["name"].lower().endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    asset_name = asset["name"]
                    break
            
            if not download_url:
                print("Nenhum asset .exe encontrado na release.")
                return

            # Janela invisível para diálogo
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            
            if not messagebox.askyesno("Atualização Disponível", 
                                     f"Uma nova versão ({release_data['tag_name']}) está disponível.\n\n"
                                     f"Deseja atualizar agora?\n(O download pode levar alguns segundos)",
                                     parent=root):
                root.destroy()
                return

            # Caminho temporário para o novo arquivo
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, "update_new.exe")
            
            # Download via requests com stream
            response = requests.get(download_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            # Tentar baixar e salvar
            with open(new_exe_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self._apply_update(new_exe_path)
            root.destroy()
            
        except Exception as e:
            root = Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showerror("Erro na Atualização", f"Ocorreu um erro ao baixar a atualização:\n{e}", parent=root)
            root.destroy()

    def _apply_update(self, new_exe_path):
        """Cria o script .bat para substituir o arquivo e reiniciar o app."""
        # sys.executable é o caminho real do .exe quando compilado
        current_exe = os.path.abspath(sys.executable)
        exe_dir = os.path.dirname(current_exe)
        exe_filename = os.path.basename(current_exe)
        
        batch_path = os.path.join(tempfile.gettempdir(), "update_script.bat")
        
        # O script .bat aguarda o encerramento, tenta deletar em loop e reinicia
        batch_content = f"""@echo off
setlocal enabledelayedexpansion
title Atualizador de Sistema
echo Aguardando o encerramento do aplicativo...

:wait_close
taskkill /f /im "{exe_filename}" >nul 2>&1
timeout /t 1 /nobreak >nul

:retry_del
if exist "{current_exe}" (
    del /f /q "{current_exe}" >nul 2>&1
    if exist "{current_exe}" (
        timeout /t 1 /nobreak >nul
        goto retry_del
    )
)

echo Instalando nova versao...
move /y "{new_exe_path}" "{current_exe}" >nul 2>&1

echo Reiniciando...
start "" "{current_exe}"
del "%~f0" & exit
"""

        with open(batch_path, "w") as f:
            f.write(batch_content)

        # Executa o script .bat em segundo plano e encerra o app atual
        subprocess.Popen(["cmd.exe", "/c", batch_path], 
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        sys.exit(0)

def run_auto_update(owner, repo, version, exe_name):
    """Função auxiliar que só executa se o app estiver compilado."""
    # Evita que o script tente se atualizar enquanto roda via Python puro
    if not getattr(sys, 'frozen', False):
        print("Rodando via script (não compilado). Ignorando auto-update.")
        return
        
    updater = Updater(owner, repo, version, exe_name)
    update_data = updater.check_for_updates()
    if update_data:
        updater.download_and_install(update_data)

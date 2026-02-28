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

    def check_for_updates(self):
        """Verifica se há uma nova versão disponível no GitHub Releases."""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            
            latest_version = release_data["tag_name"].lstrip("v")
            
            if parse_version(latest_version) > parse_version(self.current_version):
                return release_data
            return None
        except Exception as e:
            print(f"Erro ao verificar atualizações: {e}")
            return None

    def download_and_install(self, release_data):
        """Baixa o novo executável e inicia o processo de substituição."""
        try:
            # Encontrar o asset que é um .exe
            assets = release_data.get("assets", [])
            download_url = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    download_url = asset["browser_download_url"]
                    break
            
            if not download_url:
                messagebox.showerror("Erro", "Nenhum executável encontrado na release mais recente.")
                return

            # Criar janela de aviso de download
            root = Tk()
            root.withdraw()
            
            if not messagebox.askyesno("Atualização Disponível", 
                                     f"Uma nova versão ({release_data['tag_name']}) está disponível.\n\n"
                                     f"Deseja atualizar agora?"):
                root.destroy()
                return

            # Caminho temporário para o novo arquivo
            temp_dir = tempfile.gettempdir()
            new_exe_path = os.path.join(temp_dir, "update_new.exe")
            
            # Download
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(new_exe_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self._apply_update(new_exe_path)
            root.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro na Atualização", f"Ocorreu um erro ao baixar a atualização:\n{e}")

    def _apply_update(self, new_exe_path):
        """Cria o script .bat para substituir o arquivo e reiniciar o app."""
        current_exe = os.path.abspath(sys.argv[0])
        batch_path = os.path.join(tempfile.gettempdir(), "update_script.bat")
        
        # O script .bat aguarda o encerramento, deleta o antigo, move o novo e reinicia
        batch_content = f"""@echo off
setlocal
taskkill /f /im "{os.path.basename(current_exe)}" >nul 2>&1
timeout /t 2 /nobreak >nul
:retry
del /f /q "{current_exe}"
if exist "{current_exe}" (
    timeout /t 1 /nobreak >nul
    goto retry
)
move /y "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""

        with open(batch_path, "w") as f:
            f.write(batch_content)

        # Executa o script .bat em segundo plano e encerra o app atual
        subprocess.Popen(["cmd.exe", "/c", batch_path], 
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        sys.exit(0)

def run_auto_update(owner, repo, version, exe_name):
    """Função auxiliar para facilitar a chamada no início do app."""
    updater = Updater(owner, repo, version, exe_name)
    update_data = updater.check_for_updates()
    if update_data:
        updater.download_and_install(update_data)

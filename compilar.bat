@echo off
echo Instalando dependencias...
pip install requests packaging pyinstaller
echo.
echo Compilando o AutoJJS...
pyinstaller --onefile --noconsole --name "AutoJJS" --icon=NONE main.py
echo.
echo Compilacao concluida! O arquivo esta na pasta 'dist'.
pause

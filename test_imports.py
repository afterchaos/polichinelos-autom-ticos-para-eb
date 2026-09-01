#!/usr/bin/env python3

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleOutputCP(65001)

try:
    print("Testing imports...")
    from config_manager import ConfigManager
    print("config_manager imported successfully")
    
    from auto_typer import AutoTyper
    print("auto_typer imported successfully")
    
    import customtkinter as ctk
    print("customtkinter imported successfully")
    
    import pyperclip
    print("pyperclip imported successfully")
    
    from pynput import keyboard
    print("pynput.keyboard imported successfully")
    
    from pynput.keyboard import Controller
    print("pynput.keyboard.Controller imported successfully")
    
    print("\nAll imports successful!")
    
    config = ConfigManager()
    print(f"ConfigManager initialized")
    print(f"  Config file: {config.config_file}")
    print(f"  Settings: {config.config}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

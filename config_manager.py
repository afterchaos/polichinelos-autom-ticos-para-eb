import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".autojjs"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self):
        return {
            "main": {
                "start_num": 1,
                "end_num": 10000,
                "trigger_key": "TAB",
                "exclamation_format": "junta"
            },
            "auto_type": {
                "enabled": False,
                "hotkey": "f9",
                "delay_ms": 50,
                "auto_send_enter": True,
                "start_num": 1,
                "end_num": 10000
            },
            "semi_auto": {
                "enabled": False,
                "hotkey": "f8",
                "prefix_key": ";",
                "delay_ms": 50,
                "auto_send_enter": True,
                "start_num": 1,
                "end_num": 10000,
                "auto_skip_space": True
            }
        }

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()

    def get_section(self, section):
        return self.config.get(section, {})

    def set_section(self, section, data):
        self.config[section] = data
        self.save()

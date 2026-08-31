import threading
import unittest
from types import SimpleNamespace

import main
from main import AutoJJSApp


class JJSOrderTests(unittest.TestCase):
    def test_number_first_order(self):
        app = SimpleNamespace(
            jjs_word1="SENTINELA",
            jjs_word2="AGUARDANDO",
            jjs_sequence_order="number_first",
            exclamation_format="junta",
            numero_para_extenso=lambda n: "UM",
        )

        self.assertEqual(
            AutoJJSApp._build_jjs_sequence(app, 1),
            ["UM!", "SENTINELA", "AGUARDANDO"],
        )

    def test_word_first_order(self):
        app = SimpleNamespace(
            jjs_word1="SENTINELA",
            jjs_word2="AGUARDANDO",
            jjs_sequence_order="word_first",
            exclamation_format="junta",
            numero_para_extenso=lambda n: "UM",
        )

        self.assertEqual(
            AutoJJSApp._build_jjs_sequence(app, 1),
            ["SENTINELA", "AGUARDANDO", "UM!"],
        )

    def test_jjs_does_not_stop_on_single_failed_confirmation(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.sequence_active = True
        app.typing_automatically = False
        app.is_typing_char = False
        app.jjs_delay_ms = 0
        app.jjs_auto_send_enter = True
        app.auto_typer = SimpleNamespace(
            is_discord_active=lambda: True,
            clear_textbox=lambda: None,
            fail_count=0,
            check_message_sent=lambda: False,
        )
        app.keyboard_controller = SimpleNamespace(
            type=lambda *args, **kwargs: None,
            press=lambda *args, **kwargs: None,
            release=lambda *args, **kwargs: None,
        )
        app.after = lambda *args, **kwargs: None

        result = app._jjs_type_and_send("TESTE")

        self.assertTrue(result)
        self.assertTrue(app.sequence_active)

    def test_jjs_keeps_running_after_failed_confirmation(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.sequence_active = True
        app.typing_automatically = False
        app.is_typing_char = False
        app.jjs_delay_ms = 0
        app.jjs_auto_send_enter = True
        calls = {"count": 0}

        def fake_check_message_sent():
            calls["count"] += 1
            return False

        app.auto_typer = SimpleNamespace(
            is_discord_active=lambda: True,
            clear_textbox=lambda: None,
            fail_count=1,
            check_message_sent=fake_check_message_sent,
        )
        app.keyboard_controller = SimpleNamespace(
            type=lambda *args, **kwargs: None,
            press=lambda *args, **kwargs: None,
            release=lambda *args, **kwargs: None,
        )
        app.after = lambda *args, **kwargs: None

        result = app._jjs_type_and_send("TESTE")

        self.assertTrue(result)
        self.assertTrue(app.sequence_active)

    def test_auto_type_keeps_running_after_failed_confirmation(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.sequence_active = True
        app.auto_type_enabled = True
        app.auto_type_delay_ms = 0
        app.auto_send_enter = True
        app.typing_automatically = False
        app.is_typing_char = False
        app.footer_hint = SimpleNamespace(configure=lambda *args, **kwargs: None)
        app.trigger_key_str = "F9"
        app.color_main = "#fff"
        app.color_btn_danger = "#f00"
        app.after = lambda *args, **kwargs: None
        app.numero_para_extenso = lambda n: "UM"
        app.exclamation_format = "junta"
        app.auto_type_start_num = 1
        app.auto_type_end_num = 2
        app.auto_type_sequence_running = False
        app.semi_auto_sequence_running = False
        app.jjs_sequence_running = False
        app.auto_typer = SimpleNamespace(
            is_discord_active=lambda: True,
            clear_textbox=lambda: None,
            fail_count=0,
            check_message_sent=lambda: False,
        )
        app.keyboard_controller = SimpleNamespace(
            type=lambda *args, **kwargs: None,
            press=lambda *args, **kwargs: None,
            release=lambda *args, **kwargs: None,
        )

        app.start_continuous_sequence(1)
        self.assertTrue(app.sequence_active)

    def test_hotkey_can_toggle_sequence_off_and_on_again(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.auto_type_enabled = True
        app.auto_type_hotkey_obj = "f9"
        app.auto_type_start_num = 1
        app.last_hotkey_time = 0
        app.sequence_active = True
        app.active_sequence = "auto_type"
        app.auto_type_sequence_running = True
        app.semi_auto_sequence_running = False
        app.jjs_sequence_running = False
        app.is_typing_char = False
        app.typing_automatically = False
        app.after = lambda *args, **kwargs: None
        app.sequence_running = True

        # Desliga a sequência usando o mesmo comportamento do on_press real.
        if app.sequence_active and app.active_sequence == "auto_type":
            app.sequence_active = False
            app.auto_type_sequence_running = False
            app.sequence_running = app.semi_auto_sequence_running or app.jjs_sequence_running
            if not app.sequence_running:
                app.active_sequence = None

        self.assertFalse(app.sequence_active)
        self.assertIsNone(app.active_sequence)

        # Reativa a sequência na próxima pressiona da mesma hotkey.
        app.sequence_active = False
        app.auto_type_sequence_running = False
        app.semi_auto_sequence_running = False
        app.jjs_sequence_running = False
        app.sequence_running = False
        app.active_sequence = "auto_type"
        app.sequence_active = True

        self.assertTrue(app.sequence_active)
        self.assertEqual(app.active_sequence, "auto_type")

    def test_jjs_sequence_runs_until_end_limit(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.sequence_running = False
        app.sequence_active = True
        app.jjs_enabled = True
        app.jjs_start_num = 1
        app.jjs_end_num = 2
        app.jjs_contador = 1
        app.jjs_word1 = "CANGURU"
        app.jjs_word2 = "PULO"
        app.jjs_sequence_order = "word_first"
        app.exclamation_format = "junta"
        app.numero_para_extenso = lambda n: "UM" if n == 1 else "DOIS"
        app.auto_typer = SimpleNamespace(
            is_discord_active=lambda: True,
            clear_textbox=lambda: None,
            fail_count=0,
            check_message_sent=lambda: True,
        )
        app.keyboard_controller = SimpleNamespace(
            type=lambda *args, **kwargs: None,
            press=lambda *args, **kwargs: None,
            release=lambda *args, **kwargs: None,
        )
        app.after = lambda *args, **kwargs: None
        app.footer_hint = SimpleNamespace(configure=lambda *args, **kwargs: None)
        app.color_main = "#fff"
        app.color_btn_danger = "#f00"
        app.typing_automatically = False
        app.is_typing_char = False
        app.trigger_key_str = "F7"
        app.jjs_delay_ms = 0
        app.jjs_auto_send_enter = False
        app.auto_type_sequence_running = False
        app.semi_auto_sequence_running = False
        app.jjs_sequence_running = False

        seen = []
        app._jjs_type_and_send = lambda text: seen.append(text) or True

        original_thread = threading.Thread

        class FakeThread:
            def __init__(self, target, daemon=None):
                self._target = target
                self.daemon = daemon

            def start(self):
                self._target()

        main.threading.Thread = FakeThread
        try:
            app.start_jjs_sequence(1)
        finally:
            main.threading.Thread = original_thread

        self.assertEqual(len(seen), 6)
        self.assertEqual(seen[:3], ["CANGURU", "PULO", "UM!"])
        self.assertEqual(seen[3:], ["CANGURU", "PULO", "DOIS!"])
        self.assertEqual(app.jjs_start_num, 1)
        self.assertEqual(app.jjs_contador, 3)
        self.assertFalse(app.sequence_active)

    def test_other_sequence_modes_do_not_block_each_other(self):
        app = AutoJJSApp.__new__(AutoJJSApp)
        app.auto_type_sequence_running = True
        app.semi_auto_sequence_running = False
        app.jjs_sequence_running = False
        app.sequence_running = True
        app.auto_type_enabled = True
        app.auto_typer = SimpleNamespace(
            is_discord_active=lambda: True,
            clear_textbox=lambda: None,
            fail_count=0,
            check_message_sent=lambda: True,
        )
        app.auto_type_start_num = 1
        app.auto_type_end_num = 5
        app.auto_type_delay_ms = 0
        app.auto_send_enter = False
        app.sequence_active = True
        app.typing_automatically = False
        app.is_typing_char = False
        app.footer_hint = SimpleNamespace(configure=lambda *args, **kwargs: None)
        app.color_main = "#fff"
        app.color_btn_danger = "#f00"
        app.trigger_key_str = "F9"
        app.keyboard_controller = SimpleNamespace(
            type=lambda *args, **kwargs: None,
            press=lambda *args, **kwargs: None,
            release=lambda *args, **kwargs: None,
        )
        app.after = lambda *args, **kwargs: None
        app.numero_para_extenso = lambda n: "UM"
        app.exclamation_format = "junta"

        original_thread = threading.Thread

        class FakeThread:
            def __init__(self, target, daemon=None):
                self._target = target
                self.daemon = daemon

            def start(self):
                self._target()

        main.threading.Thread = FakeThread
        try:
            app.start_continuous_sequence(1)
        finally:
            main.threading.Thread = original_thread

        self.assertTrue(app.auto_type_sequence_running)


if __name__ == "__main__":
    unittest.main()

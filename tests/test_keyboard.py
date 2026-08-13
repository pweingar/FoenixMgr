import sys
import unittest
from pathlib import Path
from unittest.mock import call
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "FoenixMgr"))

import foenix
import keyboard


class OpticalKeyboardEncodingTests(unittest.TestCase):
    def test_lowercase_a(self):
        pressed, released = keyboard.encode_optical_character("a")
        self.assertEqual(pressed[2:4], bytes([0x10, 0x04]))
        self.assertEqual(released[2:4], bytes([0x10, 0x00]))

    def test_uppercase_a_adds_left_shift(self):
        pressed, _ = keyboard.encode_optical_character("A")
        self.assertEqual(pressed[2:4], bytes([0x10, 0x84]))

    def test_run_stop(self):
        pressed, _ = keyboard.encode_optical_key("run-stop")
        self.assertEqual(pressed[14:16], bytes([0x70, 0x80]))

    def test_text_contains_press_and_release_for_each_character(self):
        self.assertEqual(len(keyboard.encode_optical_text("ab")), 4)

    def test_unknown_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown key"):
            keyboard.encode_optical_key("f13")


class KeyboardProtocolTests(unittest.TestCase):
    def setUp(self):
        self.port = foenix.FoenixDebugPort()
        self.port.write_block = Mock()

    def test_optical_snapshot_uses_staging_register(self):
        snapshot = bytes(range(16))
        self.port.inject_optical_keyboard_snapshot(snapshot)
        self.port.write_block.assert_called_once_with(0xF01DE0, snapshot)

    def test_optical_snapshot_requires_exact_size(self):
        with self.assertRaisesRegex(ValueError, "must contain 16 bytes"):
            self.port.inject_optical_keyboard_snapshot(bytes(15))

    def test_scan_codes_are_written_one_at_a_time(self):
        self.port.inject_keyboard_scan_codes([0x1C, 0xF0, 0x1C])
        self.assertEqual(
            self.port.write_block.call_args_list,
            [
                call(0xF01642, bytes([0x1C])),
                call(0xF01642, bytes([0xF0])),
                call(0xF01642, bytes([0x1C])),
            ],
        )


if __name__ == "__main__":
    unittest.main()

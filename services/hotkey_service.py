"""全域熱鍵服務。"""

from __future__ import annotations

import logging
from typing import Callable

from pynput import keyboard

logger = logging.getLogger(__name__)


def _parse_hotkey(hotkey: str) -> frozenset[keyboard.Key | keyboard.KeyCode]:
    parts = hotkey.lower().replace("+", " ").split()
    keys: set[keyboard.Key | keyboard.KeyCode] = set()
    name_map = {
        "ctrl": keyboard.Key.ctrl,
        "control": keyboard.Key.ctrl,
        "alt": keyboard.Key.alt,
        "shift": keyboard.Key.shift,
        "f1": keyboard.Key.f1,
        "f2": keyboard.Key.f2,
        "f3": keyboard.Key.f3,
        "f4": keyboard.Key.f4,
        "f5": keyboard.Key.f5,
        "f6": keyboard.Key.f6,
        "f7": keyboard.Key.f7,
        "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9,
        "f10": keyboard.Key.f10,
        "f11": keyboard.Key.f11,
        "f12": keyboard.Key.f12,
    }
    for p in parts:
        if p in name_map:
            keys.add(name_map[p])
        elif len(p) == 1:
            keys.add(keyboard.KeyCode.from_char(p))
    return frozenset(keys)


class HotkeyService:
    def __init__(self) -> None:
        self._listener: keyboard.Listener | None = None
        self._pressed: set[keyboard.Key | keyboard.KeyCode] = set()
        self._bindings: list[tuple[frozenset, Callable[[], None]]] = []
        self._fired_combos: set[frozenset] = set()

    def set_bindings(
        self,
        heal_hotkey: str,
        mana_hotkey: str,
        master_hotkey: str,
        on_heal: Callable[[], None],
        on_mana: Callable[[], None],
        on_master: Callable[[], None],
    ) -> None:
        self._bindings = [
            (_parse_hotkey(heal_hotkey), on_heal),
            (_parse_hotkey(mana_hotkey), on_mana),
            (_parse_hotkey(master_hotkey), on_master),
        ]

    def start(self) -> None:
        self.stop()
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._pressed.clear()

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        self._pressed.add(key)
        for combo, callback in self._bindings:
            if combo and combo <= self._pressed and combo not in self._fired_combos:
                self._fired_combos.add(combo)
                try:
                    callback()
                except Exception:
                    logger.exception("熱鍵回呼執行失敗")
                break

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        self._pressed.discard(key)
        for combo, _ in self._bindings:
            if combo and not (combo <= self._pressed):
                self._fired_combos.discard(combo)

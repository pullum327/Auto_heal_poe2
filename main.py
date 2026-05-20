"""POE2 自動補血/補魔 — 程式進入點。"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from config import load_config, save_config, rect_to_config
from core.capture import ScreenCapture
from core.orb_detector import OrbDetector
from services.hotkey_service import HotkeyService
from services.worker import PotionWorker
from ui.calibration_dialog import run_calibration
from ui.overlay import OverlayWindow
from ui.settings_dialog import SettingsDialog


class AppController:
    def __init__(self) -> None:
        self.qt_app = QApplication(sys.argv)
        self.config = load_config()
        self.overlay = OverlayWindow(self.config)
        self.worker = PotionWorker()
        self.hotkeys = HotkeyService()
        self._capture = ScreenCapture()
        self._settings_dialog: SettingsDialog | None = None

        self.worker.apply_config(self.config)
        self.overlay.config_changed.connect(self._on_config_changed)
        self.overlay.request_settings.connect(self._open_settings)
        self.overlay.request_calibrate_life.connect(
            lambda: self._start_calibration("life")
        )
        self.overlay.request_calibrate_mana.connect(
            lambda: self._start_calibration("mana")
        )
        self.overlay.request_quit.connect(self.qt_app.quit)
        self.worker.status_updated.connect(self.overlay.update_status)

        self._setup_hotkeys()

    def _setup_hotkeys(self) -> None:
        self.hotkeys.set_bindings(
            str(self.config.get("hotkey_heal_toggle", "f6")),
            str(self.config.get("hotkey_mana_toggle", "f7")),
            str(self.config.get("hotkey_master_toggle", "f8")),
            self.overlay.toggle_heal,
            self.overlay.toggle_mana,
            self.overlay.toggle_master,
        )
        self.hotkeys.start()

    def _on_config_changed(self, config: dict) -> None:
        self.config = config
        save_config(self.config)
        self.worker.apply_config(self.config)
        self.hotkeys.stop()
        self._setup_hotkeys()

    def _open_settings(self) -> None:
        if self._settings_dialog and self._settings_dialog.isVisible():
            self._settings_dialog.raise_()
            return
        self._settings_dialog = SettingsDialog(
            self.config,
            on_save=self._on_settings_saved,
            on_calibrate_life=lambda: self._start_calibration("life"),
            on_calibrate_mana=lambda: self._start_calibration("mana"),
            parent=self.overlay,
        )
        self._settings_dialog.show()

    def _on_settings_saved(self, config: dict) -> None:
        self.config.update(config)
        self.overlay.apply_config(self.config)
        self._on_config_changed(self.config)

    def _start_calibration(self, orb: str) -> None:
        label = "校正生命球" if orb == "life" else "校正魔力球"

        def on_done(rect: tuple[int, int, int, int] | None) -> None:
            if rect is None:
                return
            key_rect = "life_orb_rect" if orb == "life" else "mana_orb_rect"
            key_ref = "life_reference_hsv" if orb == "life" else "mana_reference_hsv"
            self.config[key_rect] = rect_to_config(rect)

            detector = OrbDetector(orb, self._capture)
            detector.set_rect(rect)
            ref = detector.capture_reference_from_rect()
            self.config[key_ref] = list(ref) if ref else None

            self._on_config_changed(self.config)
            self.overlay.apply_config(self.config)

        run_calibration(
            orb,
            label,
            float(self.config.get("orb_radius_percent", 7.5)),
            on_done,
        )

    def run(self) -> int:
        self.overlay.show()
        self.worker.start()
        code = self.qt_app.exec()
        self.worker.stop_worker()
        self.worker.wait(3000)
        self.hotkeys.stop()
        save_config(self.config)
        return code


def main() -> None:
    controller = AppController()
    sys.exit(controller.run())


if __name__ == "__main__":
    main()

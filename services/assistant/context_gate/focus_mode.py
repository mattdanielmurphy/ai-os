"""Focus Mode probe using macOS Shortcuts and system fallback."""

import logging
import subprocess
import time
from typing import Optional, Tuple

logger = logging.getLogger("assistant.context_gate.focus_mode")


class FocusModeProbe:
    def __init__(self):
        self._shortcut_name = "Get Current Focus"
        self._shortcut_supported: Optional[bool] = None
        self._last_support_check: float = 0.0

    def _is_shortcut_available(self) -> bool:
        now = time.time()
        # Cache shortcut existence for 5 minutes
        if self._shortcut_supported is not None and (now - self._last_support_check < 300):
            return self._shortcut_supported

        try:
            res = subprocess.run(
                ["shortcuts", "list"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if res.returncode == 0:
                available_shortcuts = [line.strip() for line in res.stdout.splitlines()]
                self._shortcut_supported = self._shortcut_name in available_shortcuts
            else:
                self._shortcut_supported = False
        except Exception as e:
            logger.debug(f"Failed to query shortcuts list: {e}")
            self._shortcut_supported = False

        self._last_support_check = now
        return self._shortcut_supported

    def check_focus_mode(self) -> Tuple[bool, Optional[str]]:
        """
        Checks if a macOS Focus Mode / Do Not Disturb is active.
        Returns:
            (is_focused, focus_name)
        """
        # 1. Primary: If "Get Current Focus" shortcut exists, run it
        if self._is_shortcut_available():
            try:
                res = subprocess.run(
                    ["shortcuts", "run", self._shortcut_name],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if res.returncode == 0:
                    output = res.stdout.strip()
                    if output and output.lower() not in ("off", "none", "false", "0", ""):
                        logger.info(f"Focus Mode active via shortcut: '{output}'")
                        return True, output
                    return False, None
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout running shortcut '{self._shortcut_name}', assuming available")
            except Exception as e:
                logger.debug(f"Shortcut execution error: {e}")

        # 2. Fallback probe: Check ControlCenter / Do Not Disturb assertions if queryable
        try:
            res = subprocess.run(
                ["defaults", "read", "com.apple.controlcenter", "NSStatusItem Visible FocusModes"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if res.returncode == 0 and res.stdout.strip() == "1":
                # Icon is visible in menu bar when focus is active
                logger.info("Focus Mode indicator detected active in ControlCenter")
                return True, "Active Focus Mode"
        except Exception:
            pass

        # 3. Safe fallback: assume user is available
        return False, None

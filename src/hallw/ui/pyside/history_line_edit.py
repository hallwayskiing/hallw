from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QLineEdit


class HistoryLineEdit(QLineEdit):
    """Custom QLineEdit with command history support (Up/Down arrows)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: List[str] = []
        self._history_index: int = 0

    def add_to_history(self, text: str) -> None:
        """Adds text to history if it's not empty or a duplicate of the last entry."""
        if not text:
            return
        if self._history and self._history[-1] == text:
            self._history_index = len(self._history)
            return
        self._history.append(text)
        self._history_index = len(self._history)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle Up/Down arrow keys to cycle through history."""
        if event.key() == Qt.Key_Up:
            if self._history and self._history_index > 0:
                self._history_index -= 1
                self.setText(self._history[self._history_index])
        elif event.key() == Qt.Key_Down:
            if self._history_index < len(self._history) - 1:
                self._history_index += 1
                self.setText(self._history[self._history_index])
            else:
                self._history_index = len(self._history)
                self.clear()
        else:
            super().keyPressEvent(event)

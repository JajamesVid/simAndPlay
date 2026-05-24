"""
simAndPlay — entry point.
Must set vispy backend BEFORE any PyQt6 imports.
"""
import sys
import vispy
vispy.use('pyqt6')   # must happen before importing PyQt6

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


DARK_PALETTE = {
    QPalette.ColorRole.Window:          '#0d1117',
    QPalette.ColorRole.WindowText:      '#c9d1d9',
    QPalette.ColorRole.Base:            '#161b22',
    QPalette.ColorRole.AlternateBase:   '#0d1117',
    QPalette.ColorRole.ToolTipBase:     '#161b22',
    QPalette.ColorRole.ToolTipText:     '#c9d1d9',
    QPalette.ColorRole.Text:            '#c9d1d9',
    QPalette.ColorRole.Button:          '#21262d',
    QPalette.ColorRole.ButtonText:      '#c9d1d9',
    QPalette.ColorRole.BrightText:      '#ffffff',
    QPalette.ColorRole.Highlight:       '#1f6feb',
    QPalette.ColorRole.HighlightedText: '#ffffff',
}

STYLESHEET = """
QWidget {
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}
QPushButton {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
}
QPushButton:hover  { background: #30363d; border-color: #58a6ff; }
QPushButton:pressed { background: #1f6feb; color: #ffffff; }
QScrollBar:vertical {
    background: #0d1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 4px;
    min-height: 20px;
}
"""


def build_palette() -> QPalette:
    palette = QPalette()
    for role, hex_color in DARK_PALETTE.items():
        palette.setColor(role, QColor(hex_color))
    return palette


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("simAndPlay")
    app.setStyle("Fusion")
    app.setPalette(build_palette())
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

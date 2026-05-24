"""
Main application window.
Phase 1: world loader + 3D viewport.
Phase 3+: ROS topic panel will be added on the right.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from renderer.viewport import Viewport3D


class SidePanel(QWidget):
    def __init__(self, viewport: Viewport3D, parent=None):
        super().__init__(parent)
        self.viewport = viewport
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)

        # ── Title ─────────────────────────────────────────────────────────────
        title = QLabel("simAndPlay")
        title.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #58a6ff; padding-bottom: 4px;")
        layout.addWidget(title)

        subtitle = QLabel("v0.1  ·  Phase 1")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8b949e; font-size: 11px; padding-bottom: 12px;")
        layout.addWidget(subtitle)

        self._separator(layout)

        # ── World section ─────────────────────────────────────────────────────
        layout.addWidget(self._section_label("WORLD"))

        self.load_btn = QPushButton("Load SDF World")
        self.load_btn.clicked.connect(self._load_world)
        layout.addWidget(self.load_btn)

        self.world_label = QLabel("No world loaded")
        self.world_label.setStyleSheet("color: #8b949e; font-size: 11px; padding: 4px 0;")
        self.world_label.setWordWrap(True)
        layout.addWidget(self.world_label)

        self._separator(layout)

        # ── Camera section ────────────────────────────────────────────────────
        layout.addWidget(self._section_label("CAMERA"))

        reset_btn = QPushButton("Reset View  [R]")
        reset_btn.clicked.connect(self.viewport.reset_camera)
        layout.addWidget(reset_btn)

        hint = QLabel("🖱 Drag: orbit\n🖱 Scroll: zoom\n🖱 Right: pan")
        hint.setStyleSheet("color: #8b949e; font-size: 11px; padding: 6px 0;")
        layout.addWidget(hint)

        self._separator(layout)

        # ── Topics section (placeholder for Phase 3) ──────────────────────────
        layout.addWidget(self._section_label("ROS TOPICS"))
        placeholder = QLabel("Connect to ROS\n(Phase 3)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(
            "color: #30363d; font-size: 11px; border: 1px dashed #30363d;"
            "border-radius: 4px; padding: 16px; margin: 4px 0;"
        )
        layout.addWidget(placeholder)

        layout.addStretch()

        # ── Status bar ────────────────────────────────────────────────────────
        self._separator(layout)
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #3fb950; font-size: 11px;")
        layout.addWidget(self.status_label)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_world(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open SDF World", "", "SDF Files (*.sdf *.world)"
        )
        if not path:
            return
        self.status_label.setText("Loading...")
        self.status_label.setStyleSheet("color: #d29922; font-size: 11px;")
        try:
            self.viewport.load_sdf(path)
            name = os.path.basename(path)
            self.world_label.setText(name)
            self.world_label.setStyleSheet("color: #3fb950; font-size: 11px; padding: 4px 0;")
            self.status_label.setText("World loaded")
            self.status_label.setStyleSheet("color: #3fb950; font-size: 11px;")
        except Exception as e:
            self.world_label.setText(f"Error: {e}")
            self.world_label.setStyleSheet("color: #f85149; font-size: 11px; padding: 4px 0;")
            self.status_label.setText("Error loading world")
            self.status_label.setStyleSheet("color: #f85149; font-size: 11px;")

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #8b949e; font-size: 10px; font-weight: bold; padding-top: 4px;")
        return lbl

    def _separator(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #21262d;")
        layout.addWidget(line)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("simAndPlay")
        self.setMinimumSize(1280, 720)
        self.resize(1400, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 3D viewport (main area)
        self.viewport = Viewport3D()
        layout.addWidget(self.viewport, stretch=1)

        # Vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #21262d;")
        layout.addWidget(sep)

        # Side panel
        self.panel = SidePanel(self.viewport)
        layout.addWidget(self.panel)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_R:
            self.viewport.reset_camera()
        super().keyPressEvent(event)

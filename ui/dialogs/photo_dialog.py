import webbrowser
from typing import Any, Dict, Optional

import requests
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QVBoxLayout


class LargeImageLoaderThread(QThread):
    loaded = Signal(bytes)
    failed = Signal()

    def __init__(self, image_url: str) -> None:
        super().__init__()
        self.image_url = image_url

    def run(self) -> None:
        try:
            response = requests.get(self.image_url, timeout=12)
            response.raise_for_status()
            self.loaded.emit(response.content)
        except requests.RequestException:
            self.failed.emit()


class PhotoDialog(QDialog):
    def __init__(self, photo: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.photo = photo
        self.loader_thread: Optional[LargeImageLoaderThread] = None
        self.setWindowTitle("Detalhes da Foto")
        self.resize(720, 620)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout()

        self.image_label = QLabel("Carregando imagem...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(360)
        self.image_label.setStyleSheet("background:#f0f3f7; border-radius:8px; color:#5f6d7a;")
        self._load_large_image()
        root_layout.addWidget(self.image_label)

        details_layout = QGridLayout()
        fields = [
            ("ALT", self.photo.get("alt", "-")),
            ("Largura", str(self.photo.get("width", "-"))),
            ("Altura", str(self.photo.get("height", "-"))),
            ("Fotografo", self.photo.get("photographer", "-")),
        ]
        for row, (label, value) in enumerate(fields):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight:700;")
            value_widget = QLabel(value or "-")
            value_widget.setWordWrap(True)
            details_layout.addWidget(label_widget, row, 0)
            details_layout.addWidget(value_widget, row, 1)

        root_layout.addLayout(details_layout)

        photographer_url = self.photo.get("photographer_url", "")
        link_button = QPushButton("Abrir perfil do fotografo")
        link_button.setEnabled(bool(photographer_url))
        link_button.clicked.connect(lambda: self._open_link(photographer_url))
        root_layout.addWidget(link_button)

        self.setLayout(root_layout)

    def _load_large_image(self) -> None:
        image_url = self.photo.get("src", {}).get("large2x") or self.photo.get("src", {}).get("large")
        if not image_url:
            self.image_label.setText("Imagem indisponivel")
            return

        self.loader_thread = LargeImageLoaderThread(image_url)
        self.loader_thread.loaded.connect(self._on_large_image_loaded)
        self.loader_thread.failed.connect(self._on_large_image_failed)
        self.loader_thread.start()

    def _on_large_image_loaded(self, image_data: bytes) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.image_label.setPixmap(
            pixmap.scaled(
                680,
                380,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def _on_large_image_failed(self) -> None:
        self.image_label.setText("Falha ao carregar imagem")

    @staticmethod
    def _open_link(url: str) -> None:
        if not url:
            return
        webbrowser.open(url)

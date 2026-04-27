from typing import Any, Dict, Optional

import requests
from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

IMAGE_TIMEOUT = 10


class ImageLoaderThread(QThread):
    loaded = Signal(bytes)
    failed = Signal()

    def __init__(self, image_url: str) -> None:
        super().__init__()
        self.image_url = image_url

    def run(self) -> None:
        try:
            response = requests.get(self.image_url, timeout=IMAGE_TIMEOUT)
            response.raise_for_status()
            self.loaded.emit(response.content)
        except requests.RequestException:
            self.failed.emit()


class PhotoCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, photo: Dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.photo = photo
        self.loader_thread: Optional[ImageLoaderThread] = None

        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("photo-card")
        self.setStyleSheet(
            """
            QFrame#photo-card {
                border: 1px solid #d9dee8;
                border-radius: 10px;
                background-color: #ffffff;
                padding: 8px;
            }
            QFrame#photo-card:hover {
                border: 1px solid #7a8ba3;
                background-color: #f7f9fc;
            }
            """
        )

        self.image_label = QLabel("Carregando imagem...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(140)
        self.image_label.setStyleSheet(
            "background:#eef2f7; border-radius:8px; color:#617183; padding:6px;"
        )

        photographer = self.photo.get("photographer", "Desconhecido")
        self.photographer_label = QLabel(photographer)
        self.photographer_label.setWordWrap(True)
        self.photographer_label.setStyleSheet("font-weight:600; color:#253345; margin-top:6px;")

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.photographer_label)
        self.setLayout(layout)

        self._load_image()

    def _load_image(self) -> None:
        image_url = self.photo.get("src", {}).get("medium")
        if not image_url:
            self.image_label.setText("Imagem indisponivel")
            return

        self.loader_thread = ImageLoaderThread(image_url)
        self.loader_thread.loaded.connect(self._on_image_loaded)
        self.loader_thread.failed.connect(self._on_image_failed)
        self.loader_thread.start()

    def _on_image_loaded(self, image_data: bytes) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        scaled = pixmap.scaled(
            280,
            180,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def _on_image_failed(self) -> None:
        self.image_label.setText("Falha ao carregar imagem")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.photo)
        super().mousePressEvent(event)

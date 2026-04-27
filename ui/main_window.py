from typing import Any, Dict, List, Optional

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.pexels_service import PexelsServiceError, fetch_curated_photos
from ui.components.card import PhotoCard
from ui.dialogs.photo_dialog import PhotoDialog
from utils.exporter import export_photos_to_csv


class CuratedPhotosWorker(QThread):
    success = Signal(list)
    failed = Signal(str)

    def __init__(self, page: int, per_page: int = 20) -> None:
        super().__init__()
        self.page = page
        self.per_page = per_page

    def run(self) -> None:
        try:
            photos = fetch_curated_photos(page=self.page, per_page=self.per_page)
            self.success.emit(photos)
        except PexelsServiceError as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    GRID_COLUMNS = 3

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Galeria Pexels")
        self.resize(1100, 760)

        self.current_page = 1
        self.photos: List[Dict[str, Any]] = []
        self.worker: Optional[CuratedPhotosWorker] = None

        self._build_ui()
        self.load_photos(reset=True)

    def _build_ui(self) -> None:
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        actions_layout = QHBoxLayout()

        self.export_button = QPushButton("Exportar relatorio")
        self.export_button.clicked.connect(self.export_report)
        actions_layout.addWidget(self.export_button)

        self.load_more_button = QPushButton("Carregar mais")
        self.load_more_button.clicked.connect(self.load_next_page)
        actions_layout.addWidget(self.load_more_button)
        actions_layout.addStretch()

        main_layout.addLayout(actions_layout)

        self.loading_indicator = QProgressBar()
        self.loading_indicator.setRange(0, 0)
        self.loading_indicator.setVisible(False)
        main_layout.addWidget(self.loading_indicator)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #46566b;")
        main_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(6, 6, 6, 6)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area)

        self.setStyleSheet(
            """
            QMainWindow { background: #f4f7fb; }
            QPushButton {
                background-color: #2f6fed;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #285fcb; }
            QPushButton:disabled { background-color: #9db5e8; color: #edf1f8; }
            QScrollArea {
                background: transparent;
                border: none;
            }
            """
        )

        self.setCentralWidget(container)

    def load_photos(self, reset: bool = False) -> None:
        if self.worker and self.worker.isRunning():
            return

        if reset:
            self.current_page = 1
            self.photos.clear()
            self._clear_grid()

        self._set_loading_state(True)
        self.status_label.setText(f"Carregando pagina {self.current_page}...")

        self.worker = CuratedPhotosWorker(page=self.current_page, per_page=20)
        self.worker.success.connect(self._on_photos_loaded)
        self.worker.failed.connect(self._on_loading_failed)
        self.worker.finished.connect(lambda: self._set_loading_state(False))
        self.worker.start()

    def load_next_page(self) -> None:
        self.current_page += 1
        self.load_photos(reset=False)

    def _on_photos_loaded(self, page_photos: List[Dict[str, Any]]) -> None:
        self.photos.extend(page_photos)
        self._render_grid()
        self.status_label.setText(f"{len(self.photos)} fotos carregadas.")
        if not page_photos:
            self.load_more_button.setEnabled(False)
            self.status_label.setText("Nao ha mais resultados disponiveis.")

    def _on_loading_failed(self, message: str) -> None:
        if self.current_page > 1:
            self.current_page -= 1
        QMessageBox.critical(self, "Erro ao carregar fotos", message)
        self.status_label.setText("Falha ao carregar dados da API.")

    def _render_grid(self) -> None:
        self._clear_grid()
        for index, photo in enumerate(self.photos):
            row = index // self.GRID_COLUMNS
            col = index % self.GRID_COLUMNS
            card = PhotoCard(photo)
            card.clicked.connect(self.open_photo_details)
            self.grid_layout.addWidget(card, row, col)

    def _clear_grid(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _set_loading_state(self, loading: bool) -> None:
        self.loading_indicator.setVisible(loading)
        self.load_more_button.setDisabled(loading)
        self.export_button.setDisabled(loading)

    def open_photo_details(self, photo: Dict[str, Any]) -> None:
        dialog = PhotoDialog(photo, self)
        dialog.exec()

    def export_report(self) -> None:
        if not self.photos:
            QMessageBox.information(self, "Exportacao", "Nao ha fotos para exportar ainda.")
            return

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio CSV",
            "relatorio_pexels.csv",
            "Arquivos CSV (*.csv)",
        )
        if not output_path:
            return

        exported_path = export_photos_to_csv(self.photos, output_path)
        QMessageBox.information(self, "Exportacao", f"Relatorio salvo em:\n{exported_path}")

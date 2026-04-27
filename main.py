import sys

from PySide6.QtWidgets import QApplication, QMessageBox


def run() -> int:
    app = QApplication(sys.argv)
    try:
        from ui.main_window import MainWindow

        window = MainWindow()
    except RuntimeError as exc:
        QMessageBox.critical(None, "Configuracao invalida", str(exc))
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())

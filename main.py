
from src.gui.app import App
from src.settings.settings import settings_instance
import sys
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
window = App(settings_instance)
sys.exit(app.exec())
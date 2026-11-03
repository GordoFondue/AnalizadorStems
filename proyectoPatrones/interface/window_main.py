import sys
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget

from interface.librery import Librery
from interface.separacion import Separacion
from interface.clasificacion import ClasificacionHMM

class WindowMain(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analizador de Stems y Patrones Musicales")
        self.setMinimumSize(1000, 700)

        self._inicializar_ui()

    def _inicializar_ui(self):
        widget_central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #121212;
            }
            QTabBar::tab {
                background-color: #181818;
                color: #a0a0a0;
                padding: 12px 18px;
                margin: 2px 0px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #282828;
                color: #ffffff;
                border-right: 3px solid #1db954;
            }
            QTabBar::tab:hover {
                background-color: #202020;
                color: #ffffff;
            }
        """)

        self.pestana_libreria = Librery()
        self.pestana_separacion = Separacion()
        self.pestana_clasificacion = ClasificacionHMM()

        self.tabs.addTab(self.pestana_libreria, "Librería")
        self.tabs.addTab(self.pestana_separacion, "Separación de Stems")
        self.tabs.addTab(self.pestana_clasificacion, "Clasificación HMM")

        layout.addWidget(self.tabs)
        widget_central.setLayout(layout)
        self.setCentralWidget(widget_central)

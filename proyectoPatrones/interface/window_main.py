import sys
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget

from interface.librery import Librery
from interface.separacion import Separacion


# -*- coding: utf-8 -*-
class WindowMain (QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Analizador de Stems")
		self.setMinimumSize(1000, 700)

		self._inicializar_ui()

	def _inicializar_ui(self):
		self.tabs= QTabWidget()

		self.tabs.setTabPosition(QTabWidget.TabPosition.West)

		self.tabs.setStyleSheet("""
			QTabWidget::pane {
				border: none;
				background-color: #121212;
			}
			QTabBar::tab{
				background-color: #181818;
				color: #a0a0a0;
				padding: 12px 18px 
				margin:2px 0px;
				border-top-right-radius: 6px;
				border-bottom-right-radius: 6px;
				font-weight: bold;
			}
			QTabBar::selected{
				background-color: #282828;
				color: #ffffff;
				border-right: 3px solid #1db954;
			}
			QTabBar::tab:hover {
				background-color: #202020;
				color: #ffffff;
				
			}

		""")
		
		self.setCentralWidget(self.tabs)

		self.pestana_db = Librery()
		self.tabs.addTab(self.pestana_db, "Librería")

		self.pestana_separacion = Separacion()
		self.tabs.addTab(self.pestana_separacion, "Separación")

		

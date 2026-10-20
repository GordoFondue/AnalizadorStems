import sys
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget
from interface.librery import Librery

class WindowMain (QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Analizador de Steams")
		self.setMinimumSize(950, 600)

		self._inicializar_ui()

	def _inicializar_ui(self):
		self.tabs= QTabWidget()

		self.tabs.setTabPosition(QTabWidget.TabPosition.East)
		
		self.setCentralWidget(self.tabs)

		self.pestana_db = Librery()
		self.tabs.addTab(self.pestana_db, "Canciones")

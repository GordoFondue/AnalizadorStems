import sys
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget
from interface.librery import Librery

class WindowMain (QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Analizador de Steams")
		self.setMinimumSize(800, 500)

		self._inicializar_ui()

	def _inicializar_ui(self):
		self.tabs= QTabWidget()
		self.setCentralWidget(self.tabs)

		self.pestana_inicio = QWidget()
		layout_inicio = QVBoxLayout()
		layout_inicio.addWidget(QLabel("Bienvenido al sistema musical"))
		self.pestana_inicio.setLayout(layout_inicio)

		self.tabs.addTab(self.pestana_inicio, "Libreria")

		self.pestana_db = Librery()
		self.tabs.addTab(self.pestana_db, "Canciones")

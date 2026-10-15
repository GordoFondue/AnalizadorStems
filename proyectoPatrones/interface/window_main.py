from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class WindowMain (QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Analizador de Steams")
		self.setMinimumSize(500, 400)

		self._inicializar_ui()

	def _inicializar_ui(self):

		widget_central = QWidget()
		self.setCentralWidget(widget_central)

		layout= QVBoxLayout()
		
		self.etiqueta = QLabel("Bienvenido al sistema de patrones musicales")
		self.etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.addWidget(self.etiqueta)
		
		self.boton = QPushButton ("Cargar y Analizar Pista")
		self.boton.clicked.connect(self.accion_botton)
		layout.addWidget(self.boton)
		
		widget_central.setLayout(layout)
		
	def accion_botton(self):
		self.etiqueta.setText("Conectar al backen") 
